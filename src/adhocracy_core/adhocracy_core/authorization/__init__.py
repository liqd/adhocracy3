"""ACL Authorization with support for rules mapped to adhocracy principals."""
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ACLPermitsResult
from pyramid.testing import DummyRequest
from zope.interface import implementer
from zope.component import queryMultiAdapter

from adhocracy_core.interfaces import IGroupLocator
from adhocracy_core.interfaces import IRolesUserLocator
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IRoleACLAuthorizationPolicy


@implementer(IRoleACLAuthorizationPolicy)
class RoleACLAuthorizationPolicy(ACLAuthorizationPolicy):

    """A :term:`authorization policy` supporting rules based permissions."""

    group_prefix = 'group:'
    role_prefix = 'role:'

    def permits(self, context: IResource,
                principals: list,
                permission: str) -> ACLPermitsResult:
        """Check `permission` for `context`. Read interface docstring."""
        # FIXME refactor the following two methods and move them to a custom
        # groupfinder function that is passed to the Authentication policy.
        self._add_groups_roles_to_principals(context, principals)
        self._add_user_roles_to_principals(context, principals)
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
        locator = queryMultiAdapter((context, request), IRolesUserLocator)
        if locator is None:  # for testing
            return
        for user in users:
            user_roles = locator.get_roleids(user) or []
            principals.extend(user_roles)
