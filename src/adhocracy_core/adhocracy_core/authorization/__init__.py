"""Authorization with roles/local roles mapped to adhocracy principals."""
from collections import defaultdict
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ACLPermitsResult
from pyramid.threadlocal import get_current_registry
from pyramid.traversal import lineage
from pyramid.registry import Registry
from zope.interface import implementer
from substanced.util import get_acl

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IRoleACLAuthorizationPolicy
from adhocracy_core.events import LocalRolesModified
from adhocracy_core.utils import set_acl


CREATOR_ROLEID = 'role:creator'


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


def add_acm(resource: IResource, acm: dict, registry: Registry):
    """Add permissions defined by an ACM to a resource.

    New permissions are generated from the ACM and put in front of the
    ACL list.
    """
    old_acl = get_acl(resource)
    new_acl = acm_to_acl(acm, registry) + old_acl
    set_acl(resource, new_acl, registry)
