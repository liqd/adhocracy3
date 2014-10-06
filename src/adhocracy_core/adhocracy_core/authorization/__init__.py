"""ACL Authorization with support for rules mapped to adhocracy principals."""
from collections import defaultdict
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ACLPermitsResult
from pyramid.traversal import lineage
from zope.interface import implementer

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IRoleACLAuthorizationPolicy


@implementer(IRoleACLAuthorizationPolicy)
class RoleACLAuthorizationPolicy(ACLAuthorizationPolicy):

    """A :term:`authorization policy` supporting (local) permissions rules.

    You can set :term:`local role`s if you add the `__local_roles__` attribute
    to the context object.
    The value is an dictionary with a :term:`groupid` or  :term:`userid` as key
    and a list of :term:`roleid`s as value::

        {'system.Everyone': ['role:reader']}

    `local role`s are inherited in the object hierarchy except `creator`.
    """

    local_roles_key = '__local_roles__'
    """Mapping group/user to role for the current context and its children."""
    creator_role = 'role:creator'
    """The local creator role is not inherited by context children."""

    def permits(self, context: IResource,
                principals: list,
                permission: str) -> ACLPermitsResult:
        """Check `permission` for `context`. Read interface docstring."""
        local_roles_map = self._get_local_role_candidates_from_lineage(context)
        self._add_roles_to_principals(principals, local_roles_map)
        return super().permits(context, principals, permission)

    def _get_local_role_candidates_from_lineage(self, context) -> dict:
        local_roles_map = defaultdict(set)
        for location in lineage(context):
            local_roles = getattr(location, self.local_roles_key, {})
            for principal, roles in local_roles.items():
                local_roles_map[principal].update(roles)
        return local_roles_map

    def _add_roles_to_principals(self, principals, roles_map):
        for canidate, roles in roles_map.items():
            if canidate in principals:
                if self.creator_role in roles:
                    roles.remove(self.creator_role)
                principals.extend(list(roles))
