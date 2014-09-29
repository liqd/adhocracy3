"""ACL Authorization with support for rules mapped to adhocracy principals."""
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ACLPermitsResult
from zope.interface import implementer

from adhocracy_core.interfaces import IGroupLocator
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
        self._add_groups_roles_to_principals(context, principals)
        return super().permits(context, principals, permission)

    def _add_groups_roles_to_principals(self, context, principals):
        groups = [p for p in principals if p.startswith(self.group_prefix)]
        locator = IGroupLocator(context, None)
        if locator is None:
            return  # for testing
        for group in groups:
            group_roles = locator.get_roleids(group) or []
            principals.extend(group_roles)
