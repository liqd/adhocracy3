from pyramid import testing
from pytest import fixture


class TestRuleACLAuthorizaitonPolicy:

    @fixture
    def inst(self):
        from adhocracy_core.authorization import RoleACLAuthorizationPolicy
        return RoleACLAuthorizationPolicy()

    # Default AuthorizationPolicy features

    def test_create(self, inst):
        from pyramid.interfaces import IAuthorizationPolicy
        from zope.interface.verify import verifyObject
        assert IAuthorizationPolicy.providedBy(inst)
        assert verifyObject(IAuthorizationPolicy, inst)
        assert inst.group_prefix == 'group:'
        assert inst.role_prefix == 'role:'

    def test_permits_no_acl(self, inst, context):
        from pyramid.security import ACLDenied
        result = inst.permits(context, [], 'view')
        assert not result
        assert isinstance(result, ACLDenied)

    def test_permits_acl(self, inst, context):
        from pyramid.security import Allow
        from pyramid.security import ACLAllowed
        context.__acl__ = [(Allow, 'Authenticated', 'view')]
        result = inst.permits(context, ['Authenticated'], 'view')
        assert result
        assert isinstance(result, ACLAllowed)

    def test_permits_acl_deny(self, inst, context):
        from pyramid.security import Deny
        context.__acl__ = [(Deny, 'Authenticated', 'view')]
        assert not inst.permits(context, ['Authenticated'], 'view')

    def test_permits_acl_wrong_principal(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'Authenticated', 'view')]
        assert not inst.permits(context, ['WRONG'], 'view')

    def test_permits_acl_wrong_permission(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'Authenticated', 'view')]
        assert not inst.permits(context, ['Authenticated'], 'WRONG')

    def test_permits_inherited_acl(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'Authenticated', 'view')]
        context['child'] = testing.DummyResource()
        assert inst.permits(context['child'], ['Authenticated'], 'view')

    def test_permits_inherited_acl_multiple_principals(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'Authenticated', 'view')]
        context['child'] = testing.DummyResource()
        context['child'].__acl__ = [(Allow, 'Everybody', 'view')]
        assert inst.permits(context['child'], ['Authenticated', 'Everybody'],
                            'view')

    def test_permits_inherited_acl_multiple_principals_local_deny(self, inst, context):
        from pyramid.security import Allow
        from pyramid.security import Deny
        context.__acl__ = [(Allow, 'Authenticated', 'view')]
        context['child'] = testing.DummyResource()
        context['child'].__acl__ = [(Deny, 'Everybody', 'view')]
        assert not inst.permits(context['child'], ['Authenticated', 'Everybody'],
                                'view')

    # Additional features to support group roles mapped to permissions

    def test_permits_acl_with_group_roles(self, inst, context, mock_group_locator):
        from pyramid.security import Allow
        mock_group_locator.get_roleids.return_value = ['role:admin']
        context.__acl__ = [(Allow, 'role:admin', 'view')]
        assert inst.permits(context, ['Authenticated', 'group:Admins'], 'view')
        assert mock_group_locator.get_roleids.call_args[0] == ('group:Admins',)

    def test_permits_acl_wrong_group(self, inst, context, mock_group_locator):
        from pyramid.security import Allow
        mock_group_locator.get_roleids.return_value = None
        context.__acl__ = [(Allow, 'role:admin', 'view')]
        assert not inst.permits(context, ['Authenticated', 'group:Admins'],
                                'view')

    def test_permits_acl_inherited_acl(self, inst, context, mock_group_locator):
        from pyramid.security import Allow
        mock_group_locator.get_roleids.return_value = ['role:admin']
        context.__acl__ = [(Allow, 'role:admin', 'view')]
        context['child'] = testing.DummyResource()
        assert inst.permits(context['child'], ['Authenticated', 'group:Admins'],
                            'view')
        assert mock_group_locator.get_roleids.call_args[0] == ('group:Admins',)


