"""ACL Authorization with support for rules mapped to adhocracy principals."""
from collections import defaultdict
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ACLPermitsResult
from pyramid.testing import DummyRequest
from pyramid.traversal import lineage
from zope.interface import implementer

from adhocracy_core.interfaces import IGroupLocator
from adhocracy_core.interfaces import IRolesUserLocator
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

    group_prefix = 'group:'
    role_prefix = 'role:'
    local_roles_key = '__local_roles__'

    def permits(self, context: IResource,
                principals: list,
                permission: str) -> ACLPermitsResult:
        """Check `permission` for `context`. Read interface docstring."""
        # FIXME refactor the following two methods and move them to a custom
        # groupfinder function that is passed to the Authentication policy.
        self._add_groups_roles_to_principals(context, principals)
        self._add_user_roles_to_principals(context, principals)
        self._add_local_roles_to_principals(context, principals)
        return super().permits(context, principals, permission)

    def _add_groups_roles_to_principals(self, context, principals):
        groups = [p for p in principals if p.startswith(self.group_prefix)]
        locator = IGroupLocator(context, None)
        if locator is None:
            return  # for testing
        for group in groups:
            group_roles = locator.get_roleids(group) or []
            principals.extend(group_roles)

    def _add_user_roles_to_principals(self, context, principals):
        users = [p for p in principals if
                 not p.startswith(self.group_prefix) and
                 not p.startswith(self.role_prefix) and
                 not p.startswith('system.')]
        request = DummyRequest()
        locator = request.registry.queryMultiAdapter((context, request),
                                                     IRolesUserLocator)
        if locator is None:  # for testing
            return
        for user in users:
            user_roles = locator.get_roleids(user) or []
            principals.extend(user_roles)

    def _add_local_roles_to_principals(self, context, principals):
        local_roles_map = self._get_local_role_candidates_from_lineage(context)
        creator_role = self.role_prefix + 'creator'
        for canidate, roles in local_roles_map.items():
            if canidate in principals:
                if creator_role in roles:
                    roles.remove(creator_role)
                principals.extend(list(roles))

    def _get_local_role_candidates_from_lineage(self, context) -> dict:
        local_roles_map = defaultdict(set)
        for location in lineage(context):
            local_roles = getattr(location, self.local_roles_key, {})
            for principal, roles in local_roles.items():
                local_roles_map[principal].update(roles)
        return local_roles_map
