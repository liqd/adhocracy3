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


@fixture
def set_acl_with_roles(mocker):
    return mocker.patch('adhocracy_core.authorization.'
                        '_set_acl_with_local_roles',
                        magic_spec=True)


@fixture
def set_acl(mocker):
    return mocker.patch('adhocracy_core.authorization._set_acl',
                        magic_spec=True)


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

    def test_permits_inherited_acl_multiple_principals_local_deny(self, inst,
                                                                  context):
        from pyramid.security import Allow
        from pyramid.security import Deny
        context.__acl__ = [(Allow, 'system.Authenticated', 'view')]
        context['child'] = testing.DummyResource()
        context['child'].__acl__ = [(Deny, 'Everybody', 'view')]
        assert not inst.permits(context['child'], ['system.Authenticated',
                                                   'Everybody'], 'view')

    # Additional features to support permission given by local creator role

    def test_permits_ignore_non_creator_local_roles(self, inst, context):
        from pyramid.security import Allow
        context.__acl__ = [(Allow, 'role:admin', 'view')]
        context.__local_roles__ = {'User': {'role:admin'}}
        assert not inst.permits(context, ['User'],  'view')

    def test_permits_ignore_no_creator_local_roles_no_anonymized_creator(
            self, inst, context, mocker):
        from . import CREATOR_ROLEID
        from pyramid.security import Allow
        context.__acl__ = [(Allow, CREATOR_ROLEID, 'view')]
        context.__local_roles__ = {}
        mocker.patch('adhocracy_core.authorization.get_anonymized_creator',
                     return_value='')
        assert not inst.permits(context, ['User'],  'view')

    def test_permits_add_creator_local_role(self, inst, context):
        from pyramid.security import Allow
        from . import CREATOR_ROLEID
        context.__acl__ = [(Allow, CREATOR_ROLEID, 'view')]
        context.__local_roles__ = {'User': {CREATOR_ROLEID}}
        assert inst.permits(context, ['User'], 'view')

    def test_permits_add_anonymized_creator_local_role(self, inst, context,
                                                       mocker):
        from pyramid.security import Allow
        from . import CREATOR_ROLEID
        mocker.patch('adhocracy_core.authorization.get_anonymized_creator',
                     return_value='User')
        context.__acl__ = [(Allow, CREATOR_ROLEID, 'view')]
        assert inst.permits(context, ['User'], 'view')


def test_set_local_roles_non_set_roles(context, registry):
    from . import set_local_roles
    new_roles = {'principal': []}
    with raises(AssertionError):
        set_local_roles(context, new_roles, registry)


def test_set_local_roles_new_roles(context, registry):
    from . import set_local_roles
    new_roles = {'principal': set()}
    set_local_roles(context, new_roles, registry)
    assert context.__local_roles__ is new_roles


def test_set_local_roles_non_differ_roles(context, registry):
    from . import set_local_roles
    old_roles = {'principal': set()}
    context.__local_roles__ = old_roles
    new_roles = {'principal': set()}
    set_local_roles(context, new_roles, registry)
    assert context.__local_roles__ is old_roles


def test_set_local_roles_differ_roles(context, registry):
    from . import set_local_roles
    old_roles = {'principal': set()}
    context.__local_roles__ = old_roles
    new_roles = {'principal': {'new'}}
    set_local_roles(context, new_roles, registry)
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
    set_local_roles(context, new_roles, config.registry)
    event = events[0]
    assert event.object is context
    assert event.new_local_roles == new_roles
    assert event.old_local_roles == old_roles
    assert event.registry == config.registry


def test_set_local_roles_update_acl(context, registry, set_acl_with_roles):
    from . import set_local_roles
    context.__acl__ = [('principal', 'role:admin', 'view')]
    new_roles = {'principal': {'role:admin'}}
    set_local_roles(context, new_roles, registry)
    set_acl_with_roles.assert_called_with(context,
                                          [('principal', 'role:admin', 'view')],
                                          registry)


def test_set_local_roles_removes_old_role_aces(context, registry,
                                               set_acl_with_roles):
    from . import set_local_roles
    context.__acl__ = [('Allow', 'group:admin', 'view')]
    new_roles = {}
    set_local_roles(context, new_roles, registry)
    set_acl_with_roles.assert_called_with(context, [], registry)


def test_add_local_roles_non_update_roles(context, registry):
    from . import add_local_roles
    new_roles = {'principal': []}
    with raises(AssertionError):
        add_local_roles(context, new_roles, registry)


def test_add_local_roles_new_roles(context, registry):
    from . import add_local_roles
    new_roles = {'principal': set()}
    add_local_roles(context, new_roles, registry)
    assert context.__local_roles__ == new_roles


def test_add_local_roles_non_differ_roles(context, registry):
    from . import add_local_roles
    old_roles = {'principal': set()}
    context.__local_roles__ = old_roles
    new_roles = {'principal': set()}
    add_local_roles(context, new_roles, registry)
    assert context.__local_roles__ is old_roles


def test_add_local_roles_differ_roles(context, registry):
    from . import add_local_roles
    old_roles = {'principal': {'old'}, 'principal2': set()}
    context.__local_roles__ = old_roles
    new_roles = {'principal': {'new'}}
    add_local_roles(context, new_roles, registry)
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
        mock.return_value = [('Allow', 'role:admin', 'view')]
        return mock

    def test_set_god_permissions(self, mocker, root, event, root_acl):
        from adhocracy_core import authorization
        from . import god_all_permission_ace
        mock_commit = mocker.patch('transaction.commit')
        mocker.spy(authorization, '_set_acl')
        self.call_fut(event)
        assert mock_commit.called
        assert root.__acl__[0] == god_all_permission_ace
        assert authorization._set_acl.called

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
        mocker.spy(authorization, '_set_acl')
        self.call_fut(event)
        self.call_fut(event)
        assert authorization._set_acl.call_count == 1


@mark.usefixtures('integration')
def test_get_root_base_acl():
    from . import _get_root_base_acl
    acl = _get_root_base_acl()
    assert acl[0] == ('Allow', 'role:admin', 'edit')


def test_create_fake_god_request(registry):
    from . import create_fake_god_request
    req = create_fake_god_request(registry)
    assert req.__cached_principals__ == ['role:god']


class TestSetACLWithLocalRoles:

    @fixture
    def acl_lineage(self, mocker):
        return mocker.patch('adhocracy_core.authorization.get_acl_lineage',
                            magic_spec=True,
                            return_value=[])

    @fixture
    def roles_all(self, mocker):
        return mocker.patch('adhocracy_core.authorization.get_local_roles_all',
                            magic_spec=True,
                            return_value={})

    @fixture
    def _set_acl(self, mocker):
        return mocker.patch('adhocracy_core.authorization._set_acl',
                            magic_spec=True)

    def call_fut(self, *args):
        from . import _set_acl_with_local_roles
        return _set_acl_with_local_roles(*args)

    def test_set_acl(self, context, acl_lineage, roles_all, _set_acl, registry):
        acl_lineage.return_value = []
        roles_all.return_value = {}
        self.call_fut(context, [('Allow', 'role:admin', 'view')], registry)
        _set_acl.assert_called_with(context,
                                    [('Allow', 'role:admin', 'view')],
                                    registry=registry)

    def test_set_empty_acl(self, context, acl_lineage, roles_all, _set_acl,
                           registry):
        acl_lineage.return_value = []
        roles_all.return_value = {}
        self.call_fut(context, [], registry)
        _set_acl.assert_called_with(context, [], registry=registry)

    def test_add_role_to_local_acl(self, context, acl_lineage, roles_all,
                                   _set_acl, registry):
        acl_lineage.return_value = []
        roles_all.return_value = {'admin': {'role:admin'}}
        self.call_fut(context, [('Allow', 'role:admin', 'view')], registry)
        _set_acl.assert_called_with(context,
                                    [('Allow', 'admin', 'view'),
                                     ('Allow', 'role:admin', 'view')],
                                    registry=registry)

    def test_add_role_to_inherited_acl(self, context, acl_lineage, roles_all,
                                       _set_acl, registry):
        acl_lineage.return_value = [('Allow', 'role:admin', 'view')]
        roles_all.return_value = {'admin': {'role:admin'}}
        self.call_fut(context, [], registry)
        _set_acl.assert_called_with(context,
                                    [('Allow', 'admin', 'view')],
                                    registry=registry)

    def test_dont_add_role_if_not_matching(self, context, acl_lineage, roles_all,
                                           _set_acl, registry):
        acl_lineage.return_value = [('Allow', 'role:admin', 'view')]
        roles_all.return_value = {'User': {'role:participant'}}
        self.call_fut(context, [], registry)
        _set_acl.assert_called_with(context, [], registry=registry)

    def test_dont_add_role_if_creator(self, context, acl_lineage, roles_all,
                                      _set_acl, registry):
        from . import CREATOR_ROLEID
        acl_lineage.return_value = [('Allow', CREATOR_ROLEID, 'view')]
        roles_all.return_value = {'admin': {CREATOR_ROLEID}}
        self.call_fut(context, [], registry)
        _set_acl.assert_called_with(context, [], registry=registry)

    def test_dont_add_role_if_ace_exists(self, context, acl_lineage, roles_all,
                                          _set_acl, registry):
        acl_lineage.return_value = [('Allow', 'role:admin', 'view'),
                                ('Allow', 'admin', 'view')]
        roles_all.return_value = {'admin': {'role:admin'}}
        self.call_fut(context, [], registry) == []
        _set_acl.assert_called_with(context, [], registry=registry)


def test_get_acl_return_empty_list_if_no_acl(context):
    from . import get_acl
    assert get_acl(context) == []


def test_get_acl_return_acl(context):
    from . import get_acl
    context.__acl__ = [('Allow', 'Admin', 'view')]
    assert get_acl(context) == [('Allow', 'Admin', 'view')]


def test_get_acl_lineage_return_inherited_acl(context):
    from . import get_acl_lineage
    grand_parent = testing.DummyResource(__acl__=[('Allow', 'Admin', 'view')])
    grand_parent['parent'] = testing.DummyResource()
    grand_parent['parent']['child'] = context
    context.__acl__ = [('Deny', 'Admin', 'view')]
    assert get_acl_lineage(context) == [('Allow', 'Admin', 'view')]


class TestSetAcl:

    def call_fut(self, *args):
        from . import set_acl
        return set_acl(*args)

    def test_set_acl_with_local_roles(self, context, registry,
                                      set_acl_with_roles):
        self.call_fut(context, [('Allow', 'Admin', 'view')], registry)
        set_acl_with_roles.assert_called_with(context,
                                              [('Allow', 'Admin', 'view')],
                                              registry)

    @mark.parametrize('acl', [([('Allow',), 'Admin', 'view'],
                               ['Allow', ('Admin',), 'view'],
                               ['Allow', 'Admin', ('view',)])])
    def test_raise_if_ace_not_lists_of_strings(self, context, registry, acl):
        with raises(AssertionError):
            self.call_fut(context, acl, registry)


@mark.usefixtures('integration')
def test_root_acm_extensions_adapter_register(registry, context):
    from . import IRootACMExtension
    root_acm_extension = registry.getAdapter(context, IRootACMExtension)
    assert root_acm_extension == {'principals': [],
                                  'permissions': []}


class TestIsPasswordRequiredToEdit:

    def call_fut(self, *args):
        from . import is_password_required_to_edit
        return is_password_required_to_edit(*args)

    def test_false_if_no_marker_sheet(self, mock_sheet):
        assert self.call_fut(mock_sheet) is False

    def test_true_if_marker_sheet(self, mock_sheet):
        from adhocracy_core.interfaces import ISheetRequirePassword
        mock_sheet.meta = \
            mock_sheet.meta._replace(isheet=ISheetRequirePassword)
        assert self.call_fut(mock_sheet) is True


class TestIsPasswordRequiredToEditSome:

    def call_fut(self, *args):
        from . import is_password_required_to_edit_some
        return is_password_required_to_edit_some(*args)

    def test_false_if_no_marker_sheets(self, mock_sheet):
        assert self.call_fut([mock_sheet]) is False

    def test_true_if_markers_sheet(self, mock_sheet):
        from adhocracy_core.interfaces import ISheetRequirePassword
        mock_sheet.meta = \
            mock_sheet.meta._replace(isheet=ISheetRequirePassword)
        assert self.call_fut([mock_sheet]) is True
