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
        assert inst.creator_role == 'role:creator'
        assert inst.local_roles_key == '__local_roles__'

    def test_permits_no_acl(self, inst, context):
        from pyramid.security import ACLDenied
        result = inst.permits(context, [], 'view')
        assert not result
        assert isinstance(result, ACLDenied)

    def test_permits_acl(self, inst, context):
        from pyramid.security import Allow
        from pyramid.security import ACLAllowed
        context.__acl__ = [(Allow, 'system.Authenticated', 'view')]
        result = inst.permits(context, ['system.Authenticated'], 'view')
        assert result
        assert isinstance(result, ACLAllowed)

    def test_permits_acl_deny(self, inst, context):
        from pyramid.security import Deny
        context.__acl__ = [(Deny, 'system.Authenticated', 'view')]
        assert not inst.permits(context, ['system.Authenticated'], 'view')

    def test_permits_acl_wrong_principal(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'system.Authenticated', 'view')]
        assert not inst.permits(context, ['WRONG'], 'view')

    def test_permits_acl_wrong_permission(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'system.Authenticated', 'view')]
        assert not inst.permits(context, ['system.Authenticated'], 'WRONG')

    def test_permits_inherited_acl(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'system.Authenticated', 'view')]
        context['child'] = testing.DummyResource()
        assert inst.permits(context['child'], ['system.Authenticated'], 'view')

    def test_permits_inherited_acl_multiple_principals(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'system.Authenticated', 'view')]
        context['child'] = testing.DummyResource()
        context['child'].__acl__ = [(Allow, 'Everybody', 'view')]
        assert inst.permits(context['child'], ['system.Authenticated',
                                               'Everybody'], 'view')

    def test_permits_inherited_acl_multiple_principals_local_deny(self, inst, context):
        from pyramid.security import Allow
        from pyramid.security import Deny
        context.__acl__ = [(Allow, 'system.Authenticated', 'view')]
        context['child'] = testing.DummyResource()
        context['child'].__acl__ = [(Deny, 'Everybody', 'view')]
        assert not inst.permits(context['child'], ['system.Authenticated',
                                                   'Everybody'], 'view')

    # Additional features to support group roles mapped to permissions

    def test_permits_acl_with_local_roles(self, inst, context):
        from pyramid.security import Allow
        context.__local_roles__ = {'system.Authenticated': ['role:admin']}
        context.__acl__ = [(Allow, 'role:admin', 'view')]
        assert inst.permits(context, ['system.Authenticated', 'Admin',
                                      'group:Admin'],  'view')

    def test_permits_acl_with_wrong_local_roles(self, inst, context):
        from pyramid.security import Allow
        context.__local_roles__ = {'WRONG_PRINCIPAL': ['role:admin']}
        context.__acl__ = [(Allow, 'role:admin', 'view')]
        assert not inst.permits(context, ['system.Authenticated', 'Admin',
                                          'group:Admin'],  'view')

    def test_permits_acl_with_inherited_local_roles(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'role:admin', 'view'),
                           (Allow, 'role:contributor', 'add')]
        context['child'] = testing.DummyResource(
            __local_roles__={'system.Authenticated': ['role:admin']})
        context['child']['grandchild'] = testing.DummyResource(
            __local_roles__={'system.Authenticated': ['role:contributor']})
        assert inst.permits(context['child']['grandchild'],
                            ['system.Authenticated'], 'view')
        assert inst.permits(context['child']['grandchild'],
                            ['system.Authenticated'], 'add')

    def test_permits_acl_with_inherited_creator_local_role(self, inst, context):
        """We do not want to inherit the 'creator' local role."""
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'role:creator', 'view')]
        context['child'] = testing.DummyResource(
            __local_roles__={'system.Authenticated': ['role:creator']})
        context['child']['grandchild'] = testing.DummyResource()
        assert not inst.permits(context['child']['grandchild'],
                                ['system.Authenticated'], 'view')
