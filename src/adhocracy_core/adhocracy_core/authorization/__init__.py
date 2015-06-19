"""Authorization with roles/local roles mapped to adhocracy principals."""
from collections import defaultdict
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ACLPermitsResult
from pyramid.threadlocal import get_current_registry
from pyramid.traversal import lineage
from pyramid.registry import Registry
from pyramid.router import Router
from zope.interface import implementer
from substanced.util import get_acl
import substanced.util
import transaction

from adhocracy_core.utils import get_root
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IRoleACLAuthorizationPolicy
from adhocracy_core.events import LocalRolesModified


CREATOR_ROLEID = 'role:creator'

god_all_permission_ace = (Allow, 'role:god', ALL_PERMISSIONS)


@implementer(IRoleACLAuthorizationPolicy)
class RoleACLAuthorizationPolicy(ACLAuthorizationPolicy):

    """A :term:`authorization policy` supporting :term:`local role`.

    You can get/set local role mapping for an resource with
     :func:`set_local_roles` and :func:`get_local_roles`.

    The local roles are inherited by children, except the `creator` role.
    """

    def permits(self, context: IResource,
                principals: list,
                permission: str) -> ACLPermitsResult:
        """Check `permission` for `context`. Read interface docstring."""
        local_roles = get_local_roles_all(context)
        principals_with_roles = set(principals)
        for principal, roles in local_roles.items():
            if principal in principals:
                principals_with_roles.update(roles)
        return super().permits(context, principals_with_roles, permission)


def set_local_roles(resource, new_local_roles: dict, registry: Registry=None):
    """Set the :term:`local role`s mapping to ``new_local_roles``.

    :param new_local_roles: Mapping from :term:`groupid`/:term:`userid` to
                            a set of :term:`role`s for the `resource`:

                            {'system.Everyone': {'role:reader'}}

    If the resource's `local roles` and the ``new_local_roles`` differ,
    set the ``new_local_roles`` via setattr and send a
    :class:`adhocracy_core.interfaces.ILocalRolesModified` to notify others.
    """
    _assert_values_have_set_type(new_local_roles)
    old_local_roles = getattr(resource, '__local_roles__', None)
    if new_local_roles == old_local_roles:
        return None
    else:
        resource.__local_roles__ = new_local_roles
    if registry is None:
        registry = get_current_registry()
    event = LocalRolesModified(resource, new_local_roles, old_local_roles,
                               registry)
    registry.notify(event)


def _assert_values_have_set_type(mapping: dict):
    for value in mapping.values():
        assert isinstance(value, set)


def get_local_roles(resource) -> dict:
    """Return the :term:`local role`s of the resource."""
    return getattr(resource, '__local_roles__', {})


def get_local_roles_all(resource) -> dict:
    """Return the :term:`local role`s of the resource and its parents.

    The `creator`role is not inherited by children.
    """
    local_roles_all = defaultdict(set)
    local_roles_all.update(get_local_roles(resource))
    for location in lineage(resource.__parent__):
        local_roles = get_local_roles(location)
        for principal, roles in local_roles.items():
            roles_without_creator = filter(lambda x: x != CREATOR_ROLEID,
                                           roles)
            local_roles_all[principal].update(roles_without_creator)
    return local_roles_all


def acm_to_acl(acm: dict, registry: Registry) -> [str]:
    """Convert an Access Control Matrix into a pyramid ACL.

    To avoid generating too many ACE, action which are None will not
    generate an ACE.

    """
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


def set_acms_for_app_root(app: Router, acms: (dict)=()):
    """
    Set the :term:`acm`s for the `app`s root object.

    In addition all permissions are granted the god user.

    :param app: The pyramid wsgi application
    :param acms: :class:`adhocracy_core.schema.ACM` dictionaries.
                 :term:`acm`s with overriding permissions should be put
                 before :term:`acm`s with default permissions.
    """
    new_acl = [god_all_permission_ace]
    for acm in acms:
        new_acl += acm_to_acl(acm, app.registry)
    root = get_root(app)
    old_acl = get_acl(root)
    if old_acl == new_acl:
        return
    set_acl(root, new_acl, app.registry)
    transaction.commit()


def set_acl(resource: IResource, acl: list, registry=None) -> bool:
    """Set the acl and mark the resource as dirty."""
    substanced.util.set_acl(resource, acl, registry)
    resource._p_changed = True


def set_god_all_permissions(resource: IResource, registry=None) -> bool:
    """Set the god's permissions on the resource."""
    old_acl = get_acl(resource)
    new_acl = [god_all_permission_ace] + old_acl
    set_acl(resource, new_acl, registry)


def clean_acl(resource: IResource, registry=None) -> bool:
    """Remove all ACL on the resource."""
    set_acl(resource, [], registry)
