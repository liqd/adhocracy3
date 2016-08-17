from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark
from pyramid.security import Allow
from pyramid.security import Deny
from unittest.mock import Mock


@fixture
def integration(config):
    config.include('adhocracy_core.authorization')
    config.include('adhocracy_core.renderers')
    return config


class TestRuleACLAuthorizationPolicy:

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
        context.__local_roles__ = {'system.Authenticated': {'role:admin'}}
        context.__acl__ = [(Allow, 'role:admin', 'view')]
        assert inst.permits(context, ['system.Authenticated', 'Admin',
                                      'group:Admin'],  'view')

    def test_permits_acl_with_wrong_local_roles(self, inst, context):
        from pyramid.security import Allow
        context.__local_roles__ = {'WRONG_PRINCIPAL': {'role:admin'}}
        context.__acl__ = [(Allow, 'role:admin', 'view')]
        assert not inst.permits(context, ['system.Authenticated', 'Admin',
                                          'group:Admin'],  'view')

    def test_permits_acl_with_inherited_local_roles(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'role:admin', 'view'),
                           (Allow, 'role:contributor', 'add')]
        context['child'] = testing.DummyResource(
            __local_roles__={'system.Authenticated': {'role:admin'}})
        context['child']['grandchild'] = testing.DummyResource(
            __local_roles__={'system.Authenticated': {'role:contributor'}})
        assert inst.permits(context['child']['grandchild'],
                            ['system.Authenticated'], 'view')
        assert inst.permits(context['child']['grandchild'],
                            ['system.Authenticated'], 'add')

    def test_permits_acl_with_inherited_creator_local_role(self, inst, context):
        """We do not want to inherit the 'creator' local role."""
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'role:creator', 'view')]
        context['child'] = testing.DummyResource(
            __local_roles__={'system.Authenticated': {'role:creator'}})
        context['child']['grandchild'] = testing.DummyResource()

        assert not inst.permits(context['child']['grandchild'],
                                ['system.Authenticated'], 'view')


def test_set_local_roles_non_set_roles(context):
    from . import set_local_roles
    new_roles = {'principal': []}
    with raises(AssertionError):
        set_local_roles(context, new_roles)


def test_set_local_roles_new_roles(context):
    from . import set_local_roles
    new_roles = {'principal': set()}
    set_local_roles(context, new_roles)
    assert context.__local_roles__ is new_roles


def test_set_local_roles_non_differ_roles(context):
    from . import set_local_roles
    old_roles = {'principal': set()}
    context.__local_roles__ = old_roles
    new_roles = {'principal': set()}
    set_local_roles(context, new_roles)
    assert context.__local_roles__ is old_roles


def test_set_local_roles_differ_roles(context):
    from . import set_local_roles
    old_roles = {'principal': set()}
    context.__local_roles__ = old_roles
    new_roles = {'principal': {'new'}}
    set_local_roles(context, new_roles)
    assert context.__local_roles__ is new_roles


def test_set_local_roles_notify_modified(context, config):
    from adhocracy_core.interfaces import ILocalRolesModfied
    from . import set_local_roles
    events = []
    listener = lambda event: events.append(event)
    config.add_subscriber(listener, ILocalRolesModfied)
    old_roles = {'principal': set()}
    context.__local_roles__ = old_roles
    new_roles = {'principal': {'new'}}
    set_local_roles(context, new_roles, registry=config.registry)
    event = events[0]
    assert event.object is context
    assert event.new_local_roles == new_roles
    assert event.old_local_roles == old_roles
    assert event.registry == config.registry


def test_add_local_roles_non_update_roles(context):
    from . import add_local_roles
    new_roles = {'principal': []}
    with raises(AssertionError):
        add_local_roles(context, new_roles)


def test_add_local_roles_new_roles(context):
    from . import add_local_roles
    new_roles = {'principal': set()}
    add_local_roles(context, new_roles)
    assert context.__local_roles__ == new_roles


def test_add_local_roles_non_differ_roles(context):
    from . import add_local_roles
    old_roles = {'principal': set()}
    context.__local_roles__ = old_roles
    new_roles = {'principal': set()}
    add_local_roles(context, new_roles)
    assert context.__local_roles__ is old_roles


def test_add_local_roles_differ_roles(context):
    from . import add_local_roles
    old_roles = {'principal': {'old'}, 'principal2': set()}
    context.__local_roles__ = old_roles
    new_roles = {'principal': {'new'}}
    add_local_roles(context, new_roles)
    assert context.__local_roles__ == {'principal': {'old', 'new'},
                                       'principal2': set()}


def test_get_local_roles(context):
    from . import get_local_roles
    roles = {'principal': set()}
    context.__local_roles__ = roles
    assert get_local_roles(context) is roles


def test_get_local_roles_default(context):
    from . import get_local_roles
    assert get_local_roles(context) == {}


def test_get_local_roles_all_with_parents(context):
    from . import get_local_roles_all
    context.__local_roles__ = {'principal': {'role:reader'}}
    context['child'] = context.clone(__local_roles__={'principal': {'role:editor'}})
    child = context['child']
    assert get_local_roles_all(child) == {'principal': {'role:reader',
                                                        'role:editor'}}


def test_get_local_roles_all_parents_with_creator_role(context):
    from . import get_local_roles_all
    context.__local_roles__ = {'principal': {'role:creator'}}
    context['child'] = context.clone(__local_roles__={'principal': {'role:editor'}})
    child = context['child']
    assert get_local_roles_all(child) == {'principal': {'role:editor'}}


def test_acm_to_acl():
    from . import acm_to_acl
    appstruct = {'principals':           ['system.Everyone', 'role:participant', 'role:moderator'],
                 'permissions': [['view',  Allow,      Allow,          Allow],
                                 ['edit',  Deny,       None,           Allow]]}
    acl = acm_to_acl(appstruct)
    assert acl == [('Allow', 'role:moderator', 'view'),
                   ('Allow', 'role:moderator', 'edit'),
                   ('Allow', 'role:participant', 'view'),
                   ('Allow', 'system.Everyone', 'view'),
                   ('Deny', 'system.Everyone', 'edit'),
                   ]


class TestSetACMSForAppRoot:

    def call_fut(self, app):
        from . import set_acms_for_app_root
        return set_acms_for_app_root(app)

    @fixture
    def root(self, context):
        return context

    @fixture
    def mock_app(self, root, registry) -> Mock:
        from pyramid.router import Router
        app = Mock(spec=Router)()
        app.root_factory.return_value = root
        app.registry = registry
        return app

    @fixture
    def event(self, mock_app):
        event = testing.DummyResource(app=mock_app)
        return event

    @fixture
    def root_acl(self, mocker):
        mock = mocker.patch('adhocracy_core.authorization._get_root_base_acl')
        mock.return_value =[('Allow', 'role:admin', 'view')]
        return mock

    def test_set_god_permissions(self, mocker, root, event, root_acl):
        from adhocracy_core import authorization
        from . import god_all_permission_ace
        mock_commit = mocker.patch('transaction.commit')
        mocker.spy(authorization, 'set_acl')
        self.call_fut(event)
        assert mock_commit.called
        assert root.__acl__[0] == god_all_permission_ace
        assert authorization.set_acl.called

    def test_set_root_acl_after_god_permission(self, root, event, root_acl):
        self.call_fut(event)
        assert root.__acl__[1] == root_acl.return_value[0]

    def test_set_extension_acl_after_root_acl(self, root, event, registry,
                                              root_acl):
        from . import IResource
        from . import IRootACMExtension
        adapter = lambda x: {'principals':  ['moderator'],
                             'permissions': [['mypermission', 'Deny']]}
        registry.registerAdapter(adapter, (IResource,), IRootACMExtension)
        self.call_fut(event)
        assert root.__acl__[1] == ('Deny', 'role:moderator', 'mypermission')

    def test_ignore_if_acl_not_changed(self, mocker, event, root_acl):
        from adhocracy_core import authorization
        mocker.spy(authorization, 'set_acl')
        self.call_fut(event)
        self.call_fut(event)
        assert authorization.set_acl.call_count == 1


@mark.usefixtures('integration')
def test_get_root_base_acl():
    from . import _get_root_base_acl
    acl = _get_root_base_acl()
    assert acl[0] == ('Allow', 'role:admin', 'edit')


def test_set_acl_set_resource_dirty():
    """Regression test."""
    from persistent.mapping import PersistentMapping
    from . import set_acl
    resource = PersistentMapping()
    resource._p_jar = Mock()  # make _p_changed property work
    set_acl(resource, [('Deny', 'role:creator', 'edit')])
    assert resource._p_changed is True


def test_create_fake_god_request(registry):
    from . import create_fake_god_request
    req = create_fake_god_request(registry)
    assert req.__cached_principals__ == ['role:god']


class TestGetPrincipalsWithLocalRoles:

    def call_fut(self,  *args):
        from . import get_principals_with_local_roles
        return get_principals_with_local_roles(*args)

    def test_principals_with_no_local_roles(self, context):
        principals = ['system.Everyone', 'system.Authenticated']
        assert set(self.call_fut(context, principals)) == set(principals)

    def test_principals_with_wrong_local_roles(self, context):
        context.__local_roles__ = {'group:default_group': {'role:participant'}}
        principals = ['system.Everyone', 'system.Authenticated']
        assert set(self.call_fut(context, principals)) == set(principals)

    def test_principals_with_local_roles(self, context):
        context.__local_roles__ = {'group:default_group': {'role:participant'}}
        principals = ['system.Everyone', 'system.Authenticated',
                      'group:default_group']
        principals_with_roles = list(principals)
        principals_with_roles.append('role:participant')
        result = self.call_fut(context, principals)
        assert set(result) == set(principals_with_roles)

    def test_principals_with_anonymized_creator(self, context, mocker):
        mocker.patch('adhocracy_core.authorization.get_anonymized_creator',
                     return_value='userid')
        context.__local_roles__ = {}
        principals = ['system.Everyone', 'system.Authenticated',
                      'userid']
        principals_with_roles = list(principals)
        principals_with_roles.append('role:creator')
        result = self.call_fut(context, principals)
        assert set(result) == set(principals_with_roles)


@mark.usefixtures('integration')
def test_root_acm_extensions_adapter_register(registry, context):
    from . import IRootACMExtension
    root_acm_extension = registry.getAdapter(context, IRootACMExtension)
    assert root_acm_extension == {'principals': [],
                                  'permissions': []}
