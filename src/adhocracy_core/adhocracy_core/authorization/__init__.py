"""Authorization with roles/local roles mapped to adhocracy principals."""
from copy import copy
from collections import defaultdict
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.renderers import render
from pyramid.security import ACLPermitsResult
from pyramid.traversal import lineage
from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.scripting import get_root
from zope.interface import implementer
from zope.interface import Interface
from substanced.util import get_acl as _get_acl
from substanced.util import set_acl as _set_acl
from substanced.stats import statsd_timer
import transaction

from adhocracy_core.authentication import get_anonymized_creator
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetRequirePassword
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IRoleACLAuthorizationPolicy
from adhocracy_core.events import LocalRolesModified
from adhocracy_core.schema import ACEPrincipal
from adhocracy_core.schema import ROLE_PRINCIPALS
from adhocracy_core.schema import SYSTEM_PRINCIPALS
from adhocracy_core.schema import ACM


CREATOR_ROLEID = 'role:creator'

god_all_permission_ace = (Allow, 'role:god', ALL_PERMISSIONS)

root_acm_asset = 'adhocracy_core.authorization:root_permissions.yaml'


class IRootACMExtension(Interface):
    """Marker interface for extension :term:`acm` of the  application root."""


@implementer(IRootACMExtension)
def acm_extension_adapter(context: IResource) -> dict:
    """Dummy adpater to extend the `root_acm`."""
    return ACM().deserialize({})


@implementer(IRoleACLAuthorizationPolicy)
class RoleACLAuthorizationPolicy(ACLAuthorizationPolicy):

    __doc__ = IRoleACLAuthorizationPolicy.__doc__

    def permits(self, context: IResource,
                principals: list,
                permission: str) -> ACLPermitsResult:
        """Check `permission` for `context`. Read interface docstring."""
        with statsd_timer('authorization', rate=.1):
            if _is_creator(context, principals):
                principals += [CREATOR_ROLEID]
            allow = super().permits(context, principals, permission)
            return allow


def _is_creator(context: IResource, principals: list) -> bool:
    """Check if one principal of `principals` is creator of `context`."""
    local_roles = get_local_roles(context)
    anonymized_creator = get_anonymized_creator(context)
    for principal in principals:
        if CREATOR_ROLEID in local_roles.get(principal, tuple()):
            return True
        elif principal == anonymized_creator:
            return True
    else:
        return False


def set_local_roles(resource, new_local_roles: dict, registry: Registry):
    """Set the :term:`local role's <local role>` mapping to ``new_local_roles``.

    :param new_local_roles: Mapping from :term:`groupid`/:term:`userid` to
                            a set of :term:`roles <role>` for the `resource`:

                            {'system.Everyone': {'role:reader'}}

    If the resource's `local roles` and the ``new_local_roles`` differ,
    set the ``new_local_roles`` via setattr and send a
    :class:`adhocracy_core.interfaces.ILocalRolesModified` to notify others.
    The :term:`ACL` of the resource in updated with the permissions added by
    the local roles.
    """
    _assert_values_have_set_type(new_local_roles)
    _set_local_roles(resource, new_local_roles, registry)
    acl = get_acl(resource)
    acl = _remove_local_role_permissions_from_acl(acl)
    _set_acl_with_local_roles(resource, acl, registry)


def _set_local_roles(resource, new_local_roles: dict, registry: Registry):
    old_local_roles = getattr(resource, '__local_roles__', None)
    if new_local_roles == old_local_roles:
        return
    else:
        resource.__local_roles__ = new_local_roles
    event = LocalRolesModified(resource, new_local_roles, old_local_roles,
                               registry)
    registry.notify(event)


def add_local_roles(resource, additional_local_roles: dict,
                    registry: Registry):
    """Add roles to existing :term:`local role's mapping."""
    _assert_values_have_set_type(additional_local_roles)
    old_local_roles = getattr(resource, '__local_roles__', {})
    local_roles = copy(old_local_roles)
    for principal, roles in additional_local_roles.items():
        old_roles = old_local_roles.get(principal, set())
        roles.update(old_roles)
        local_roles[principal] = roles
    set_local_roles(resource, local_roles, registry)


def _assert_values_have_set_type(mapping: dict):
    for value in mapping.values():
        assert isinstance(value, set)


def get_local_roles(resource) -> dict:
    """Return the :term:`local roles <local role>` of the resource."""
    local_roles = getattr(resource, '__local_roles__', {})
    return local_roles


def get_local_roles_all(resource) -> dict:
    """Return the :term:`local roles <local role>` of the resource and its parents.

    The `creator` role is ignored.
    """
    local_roles_all = defaultdict(set)
    for location in lineage(resource):
        local_roles = get_local_roles(location)
        for principal, roles in local_roles.items():
            roles_without_creator = filter(lambda x: x != CREATOR_ROLEID,
                                           roles)
            local_roles_all[principal].update(roles_without_creator)
    return local_roles_all


def acm_to_acl(acm: dict) -> [str]:
    """Convert an Access Control Matrix into a pyramid ACL.

    To avoid generating too many ACE, action which are None will not
    generate an ACE.

    Permissions for principals with high priority are listed first and override
    succeding permissions. The order is determined by
    :py:data:`adhocracy_core.schema.ROLE_PRINCIPALS`. Pricipals with higher
    index in this list have higher priority.
    """
    acl = _migrate_acm_to_acl(acm)
    _sort_by_principal_priority(acl)
    return acl


def _migrate_acm_to_acl(acm: dict) -> dict:
    acl = []
    idx = 0
    for principal in acm['principals']:
        for permissions in acm['permissions']:
            permission_name = permissions[0]
            action = permissions[idx + 1]
            if action is not None:
                ace = (action, principal, permission_name)
                acl.append(ace)
        idx = idx + 1
    return acl


def _sort_by_principal_priority(acl: list) -> list:
    roles = ROLE_PRINCIPALS.copy()
    roles.reverse()
    systems = SYSTEM_PRINCIPALS.copy()
    systems.reverse()
    schema = ACEPrincipal()
    principals = [schema.deserialize(x) for x in roles + systems]
    acl.sort(key=lambda x: principals.index(x[1]))
    return acl


def set_acms_for_app_root(event):
    """Set/update :term:`acm`s for the root object of the pyramid application.

    :param event: this function should be used as a subscriber for the
                  :class:`pyramid.interfaces.IApplicationCreated` event.
                  That way everytime the application starts the root `acm`
                  is updated.

    The `root_acm` (:func:`root_acm_asset`) is extended by the :term:`acm`
    returned by the :class:`adhocracy_core.authorization.IRootACMExtension`
    adapter.

    In addition all permissions are granted the god user.
    """
    root, closer = get_root(event.app)
    acl = [god_all_permission_ace]
    acl += _get_root_extension_acl(root, event.app.registry)
    acl += _get_root_base_acl()
    old_acl = get_acl(root)
    if old_acl == acl:
        return
    _set_acl(root, acl, registry=event.app.registry)
    transaction.commit()
    closer()


def _get_root_base_acl() -> []:
    cstruct = render(root_acm_asset, {})
    acm = ACM().deserialize(cstruct)
    acl = acm_to_acl(acm)
    return acl


def _get_root_extension_acl(context: IResource, registry: Registry) -> []:
    acm_cstruct = registry.queryAdapter(context, IRootACMExtension)
    if acm_cstruct is None:
        return []
    else:
        acm = ACM().deserialize(acm_cstruct)
        acl = acm_to_acl(acm)
        return acl


def create_fake_god_request(registry):
    """Create a fake request issued by god."""
    from adhocracy_core.interfaces import API_ROUTE_NAME
    from collections import namedtuple
    request = Request.blank('/dummy')
    request.registry = registry
    request.matched_route = namedtuple('dummy', 'name')(name=API_ROUTE_NAME)
    request.__cached_principals__ = ['role:god']
    return request


def get_acl(resource) -> []:
    """Return the :term:`ACL` of the `resource`."""
    return _get_acl(resource, default=[])


def get_acl_lineage(resource) -> []:
    """Return :term:`ACL` of the `resource` inclusive inherited acl."""
    acl_all = []
    parent = getattr(resource, '__parent__', None)
    for location in lineage(parent):
        acl = _get_acl(location, default=[])
        for ace in acl:
            acl_all.append(ace)
    return acl_all


def set_acl(resource, acl: list, registry: Registry):
    """Add :term:`local_roles` and set the term:`ACL` of the `resource`.

    Every :term:`ACE` in the `acl` has to be a list of 3 strings.
    Permission given by :term:`local_role` are added to the existing acl.
    Manually adding :term:`ACEs` containing group principals is not allowed,
    as are used for local_role permissions.
    """
    _assert_list_of_list_of_strings(acl)
    _set_acl_with_local_roles(resource, acl, registry)


def _assert_list_of_list_of_strings(acl: list):
    for action, principal, permission in acl:
        assert isinstance(action, str)
        assert isinstance(principal, str)
        assert isinstance(permission, str)


def _set_acl_with_local_roles(resource, acl: [], registry: Registry) -> []:
    """Add :term:`local_role` permissions to the :term:`ACL`.

    The creator local role is ignored, it must not be inherited
    """
    roles_all = get_local_roles_all(resource)
    acl_all = acl + get_acl_lineage(resource)
    acl_roles = set()
    for principal, local_roles in roles_all.items():
        for ace_action, ace_principal, ace_permission in acl_all:
            if ace_principal == CREATOR_ROLEID:
                continue
            if ace_principal in local_roles:
                local_role_ace = (ace_action, principal, ace_permission)
                if local_role_ace not in acl_all:
                    acl_roles.add(local_role_ace)
    acl = list(acl_roles) + acl
    _set_acl(resource, acl, registry=registry)


def _remove_local_role_permissions_from_acl(acl: []) -> []:
    """Remove :term:`local_role` permissions from the :term:`ACL`."""
    acl_without_local_roles = []
    for ace in acl:
        _, ace_principal, _ = ace
        if 'group:' not in ace_principal:
            acl_without_local_roles.append(ace)
    return acl_without_local_roles


def is_password_required_to_edit(sheet: ISheet):
    """Check if the sheets requires a password for editing."""
    return sheet.meta.isheet.isOrExtends(ISheetRequirePassword)


def is_password_required_to_edit_some(sheets: [ISheet]):
    """Check if some of the sheets require a password for editing."""
    return any(is_password_required_to_edit(sheet) for sheet in sheets)


def includeme(config):
    """Register adapter to extend the root acm and add authorization policy."""
    config.registry.registerAdapter(acm_extension_adapter,
                                    (Interface,),
                                    IRootACMExtension)
    authz_policy = RoleACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
