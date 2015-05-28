"""Tests for the principal package."""
import unittest
from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import mark
from pytest import fixture


def test_principals_meta():
    from .principal import principals_meta
    from .principal import IPrincipalsService
    meta = principals_meta
    assert meta.iresource is IPrincipalsService
    assert meta.permission_create == 'create_service'
    assert meta.content_name == 'principals'


def test_users_meta():
    from .principal import users_meta
    from .principal import IUsersService
    meta = users_meta
    assert meta.iresource is IUsersService
    assert meta.permission_create == 'create_service'
    assert meta.content_name == 'users'


def test_groups_meta():
    from .principal import groups_meta
    from .principal import IGroupsService
    meta = groups_meta
    assert meta.iresource is IGroupsService
    assert meta.permission_create == 'create_service'
    assert meta.content_name == 'groups'


def test_user_meta():
    from .principal import user_meta
    from .principal import IUser
    from .principal import User
    import adhocracy_core.sheets
    meta = user_meta
    assert meta.iresource is IUser
    assert meta.content_class == User  # TODO do we really need this class?
    assert meta.permission_create == 'create_user'
    assert meta.is_implicit_addable is False
    assert meta.basic_sheets == [adhocracy_core.sheets.principal.IUserBasic,
                                 adhocracy_core.sheets.principal.IUserExtended,
                                 adhocracy_core.sheets.principal.IPermissions,
                                 adhocracy_core.sheets.metadata.IMetadata,
                                 adhocracy_core.sheets.pool.IPool,
                                 ]
    assert meta.extended_sheets == \
           [adhocracy_core.sheets.principal.IPasswordAuthentication,
            adhocracy_core.sheets.rate.ICanRate,
           ]
    assert meta.iresource == IUser
    assert meta.element_types == []
    assert meta.use_autonaming is True


def test_group_meta():
    from .principal import group_meta
    from .principal import IGroup
    from .principal import Group
    meta = group_meta
    assert meta.iresource is IGroup
    assert meta.content_class == Group
    assert meta.permission_create == 'create_group'
    assert meta.is_implicit_addable is False
    assert meta.element_types == []


def test_passwordresets_meta():
    from .principal import passwordresets_meta
    from .principal import IPasswordResetsService
    meta = passwordresets_meta
    assert meta.iresource is IPasswordResetsService
    assert meta.permission_create == 'create_service'
    assert meta.permission_view == "manage_password_reset"
    assert meta.content_name == 'resets'


def test_passwordreset_meta():
    import adhocracy_core.sheets
    from .principal import passwordreset_meta
    from .principal import IPasswordReset
    meta = passwordreset_meta
    assert meta.iresource is IPasswordReset
    assert meta.permission_create == 'create_password_reset'
    assert meta.permission_view == 'manage_password_reset'
    assert meta.use_autonaming_random
    assert meta.basic_sheets == [adhocracy_core.sheets.metadata.IMetadata]


@fixture
def integration(config):
    config.include('pyramid_mailer.testing')
    config.include('pyramid_mako')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.changelog')
    config.include('adhocracy_core.messaging')
    config.include('adhocracy_core.sheets.metadata')
    config.include('adhocracy_core.sheets.name')
    config.include('adhocracy_core.sheets.principal')
    config.include('adhocracy_core.resources.principal')
    config.include('adhocracy_core.resources.subscriber')


@fixture
def principals(pool_graph_catalog, registry):
    from adhocracy_core.resources.principal import IPrincipalsService
    context = pool_graph_catalog
    inst = registry.content.create(IPrincipalsService.__identifier__,
                                   parent=context)
    return inst


@mark.usefixtures('integration')
class TestPrincipalsService:

    def test_create_principals(self, principals):
        from adhocracy_core.resources.principal import IPrincipalsService
        from adhocracy_core.resources.principal import IUsersService
        from adhocracy_core.resources.principal import IGroupsService
        from adhocracy_core.resources.principal import IPasswordResetsService
        assert IPrincipalsService.providedBy(principals)
        assert 'users' in principals
        assert 'groups' in principals
        assert 'resets' in principals
        assert IUsersService.providedBy(principals['users'])
        assert IGroupsService.providedBy(principals['groups'])
        assert IPasswordResetsService.providedBy(principals['resets'])

    def test_register_services(self, principals):
        from substanced.util import find_service
        context = principals.__parent__
        assert find_service(context, 'principals', 'users')
        assert find_service(context, 'principals', 'groups')
        assert find_service(context, 'principals', 'resets')


@mark.usefixtures('integration')
class TestUser:

    def test_create_user(self, registry):
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import User

        inst = registry.content.create(IUser.__identifier__)

        assert IUser.providedBy(inst)
        assert isinstance(inst, User)

    def test_create_and_add_user(self, principals, registry):
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.sheets.principal import IPasswordAuthentication
        from adhocracy_core.sheets.principal import IUserBasic
        appstructs = {
            IUserBasic.__identifier__ : {
                'name': 'Anna Müller',
            },
            IPasswordAuthentication.__identifier__ : {
                'password': 'fodThyd2'
            },
        }
        user = registry.content.create(IUser.__identifier__,
                                       parent=principals['users'],
                                       appstructs=appstructs)
        assert principals['users']['0000000'] is user


@mark.usefixtures('integration')
class TestGroup:

    def test_create_group(self, registry):
        from adhocracy_core.resources.principal import IGroup
        inst = registry.content.create(IGroup.__identifier__)
        assert IGroup.providedBy(inst)

    def test_create_and_add_group(self, principals, registry):
        from adhocracy_core.utils import get_sheet
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import IGroup
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.sheets.name import IName
        import adhocracy_core.sheets.principal
        appstructs = {IName.__identifier__: {'name': 'Group1'},
                      adhocracy_core.sheets.principal.IGroup.__identifier__:
                           {'roles': ['reader']}}
        group = registry.content.create(IGroup.__identifier__,
                                        parent=principals['groups'],
                                        appstructs=appstructs)
        appstructs = {IPermissions.__identifier__: {'groups': [group]}}
        user = registry.content.create(IUser.__identifier__,
                                       parent=principals['users'],
                                       appstructs=appstructs)
        user.activate()
        group_sheet = get_sheet(group, adhocracy_core.sheets.principal.IGroup)
        assert principals['groups']['Group1'] is group
        assert group_sheet.get()['users'] == [user]
        assert group_sheet.get()['roles'] == ['reader']


@mark.usefixtures('integration')
class TestPasswordReset:

    def test_password_reset_reset_password(self, principals, registry):
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import IPasswordReset
        user = registry.content.create(IUser.__identifier__,
                                       parent=principals['users'],
                                       appstructs={})
        reset = registry.content.create(IPasswordReset.__identifier__,
                                        parent=principals['resets'],
                                        creator=user)
        old_password = user.password
        reset.reset_password('new_password')
        new_password = user.password
        assert old_password != new_password

    def test_password_reset_suicide_after_reset(self, principals, registry):
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import IPasswordReset
        user = registry.content.create(IUser.__identifier__,
                                       parent=principals['users'],
                                       appstructs={})
        reset = registry.content.create(IPasswordReset.__identifier__,
                                        parent=principals['resets'],
                                        creator=user)
        reset.reset_password('new_password')
        assert reset.__parent__ is None


class TestPasswordResetClass:

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    def make_one(self):
        from adhocracy_core.resources.principal import PasswordReset
        return PasswordReset()

    def test_create(self):
        from zope.interface.verify import verifyObject
        from .principal import IPasswordReset
        inst = self.make_one()
        assert IPasswordReset.providedBy(inst)
        assert verifyObject(IPasswordReset, inst)


class TestUserClass:

    def _makeOne(self):
        from adhocracy_core.resources.principal import User
        return User()

    def test_create(self):
        from zope.interface.verify import verifyObject
        from .principal import IUser
        inst = self._makeOne()
        assert IUser.providedBy(inst)
        assert verifyObject(IUser, inst)
        assert inst.email == ''
        assert inst.password == ''
        assert inst.tzname == 'UTC'
        assert inst.roles == []


class TestGroupClass:

    def _makeOne(self):
        from adhocracy_core.resources.principal import Group
        return Group()

    def test_create(self):
        from zope.interface.verify import verifyObject
        from .principal import IGroup
        inst = self._makeOne()
        assert IGroup.providedBy(inst)
        assert verifyObject(IGroup, inst)
        assert inst.roles == []


class TestUserLocatorAdapter:

    def make_one(self, context=None, request=None):
        from adhocracy_core.resources.principal import UserLocatorAdapter
        return UserLocatorAdapter(context, request)

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    @fixture
    def context(self, pool, service):
        from copy import deepcopy
        pool['principals'] = service
        pool['principals']['users'] = deepcopy(service)
        return pool

    @fixture
    def request(self, context, registry):
        request = testing.DummyRequest(context=context)
        request.registry = registry
        return request

    def test_create(self):
        from adhocracy_core.interfaces import IRolesUserLocator
        from zope.interface.verify import verifyObject
        inst = self.make_one()
        assert IRolesUserLocator.providedBy(inst)
        assert verifyObject(IRolesUserLocator, inst)

    def test_get_user_by_email_user_exists(self, context, request):
        user = testing.DummyResource(email='test@test.de')
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_user_by_email('test@test.de') is user

    def test_get_user_by_email_user_not_exists(self, context, request):
        user = testing.DummyResource(email='')
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_user_by_email('wrong@test.de') is None

    def test_get_user_by_login_user_exists(self, context, request):
        user = testing.DummyResource(name='login name')
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_user_by_login('login name') is user

    def test_get_user_by_login_user_not_exists(self, context, request):
        user = testing.DummyResource(name='')
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_user_by_login('wrong login name') is None

    def test_get_user_by_activation_path_user_exists(self, context, request):
        user = testing.DummyResource(activation_path='/activate/foo')
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_user_by_activation_path('/activate/foo') is user
        
    def test_get_user_by_activation_path_user_not_exists(self, context, request):
        user = testing.DummyResource(activation_path=None)
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_user_by_activation_path('/activate/no_such_link') is None

    def test_get_user_by_userid_user_exists(self, context, request):
        user = testing.DummyResource()
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_user_by_userid('/principals/users/User1') is user

    def test_get_user_by_userid_user_not_exists(self, context, request):
        inst = self.make_one(context, request)
        assert inst.get_user_by_userid('/principals/users/User1') is None

    def test_get_groupids_user_exists(self, context, mock_sheet, request):
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.testing import register_sheet
        group = testing.DummyResource(__name__='group1')
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        mock_sheet.get.return_value = {'groups': [group]}
        user = testing.DummyResource()
        register_sheet(user, mock_sheet, request.registry)
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_groupids('/principals/users/User1') == ['group:group1']

    def test_get_groupids_user_not_exists(self, context, request):
        inst = self.make_one(context, request)
        assert inst.get_groupids('/principals/users/User1') is None

    def test_get_role_and_group_role_ids_user_exists(self, context, request):
        inst = self.make_one(context, request)
        inst.get_user_by_userid = Mock()
        inst.get_user_by_userid.return_value = context
        inst.get_roleids = Mock()
        inst.get_roleids.return_value = ['role:admin']
        inst.get_group_roleids = Mock()
        inst.get_group_roleids.return_value = ['role:reader']
        assert inst.get_role_and_group_roleids('/principals/users/User1') ==\
               ['role:admin', 'role:reader']

    def test_get_role_and_group_roleids_user_not_exists(self, context, request):
        inst = self.make_one(context, request)
        assert inst.get_role_and_group_roleids('/principals/users/User1') is None

    def test_get_group_roleids_user_exists(self, context, mock_sheet, request):
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.testing import register_sheet
        group = testing.DummyResource(__name__='group1', roles=[])
        user = testing.DummyResource()
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        mock_sheet.get.return_value = {'groups': [group]}
        register_sheet(user, mock_sheet, request.registry)
        group.roles = ['role1']
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_group_roleids('/principals/users/User1') == ['role:role1']

    def test_get_group_roleids_user_not_exists(self, context, request):
        inst = self.make_one(context, request)
        assert inst.get_group_roleids('/principals/users/User1') is None

    def test_get_roleids_user_exists(self, context, mock_sheet, request):
        from adhocracy_core.testing import register_sheet
        user = testing.DummyResource(roles=['role1'])
        register_sheet(user, mock_sheet, request.registry)
        context['principals']['users']['User1'] = user
        inst = self.make_one(context, request)
        assert inst.get_roleids('/principals/users/User1') == ['role:role1']

    def test_get_roleids_user_not_exists(self, context, request):
        inst = self.make_one(context, request)
        assert inst.get_roleids('/principals/users/User1') is None


class UserLocatorAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy_core.content')
        self.config.include('adhocracy_core.resources.principal')
        self.context = testing.DummyResource()
        self.registry = self.config.registry

    def tearDown(self):
        testing.tearDown()

    def test_create(self):
        from adhocracy_core.interfaces import IRolesUserLocator
        assert self.registry.getMultiAdapter(
            (self.context,  testing.DummyRequest), IRolesUserLocator)


class TestGroupsAndRolesFinder:

    @fixture
    def request(self, context, registry):
        request = testing.DummyRequest(context=context)
        request.registry = registry
        return request

    def call_fut(self, userid, request):
        from adhocracy_core.resources.principal import groups_and_roles_finder
        return groups_and_roles_finder(userid, request)

    def test_userid_wrong(self, request,  mock_user_locator):
        assert self.call_fut('WRONG', request) == []
        assert mock_user_locator.get_groupids.call_args[0] == ('WRONG',)
        assert mock_user_locator.get_role_and_group_roleids.call_args[0] == ('WRONG',)

    def test_userid_with_roles(self, request, mock_user_locator):
        mock_user_locator.get_role_and_group_roleids.return_value = ['role:reader']
        assert self.call_fut('userid', request) == ['role:reader']

    def test_userid_with_groups_and_group_roles(self, request, mock_user_locator):
        mock_user_locator.get_role_and_group_roleids.return_value = ['group:Readers']
        assert self.call_fut('userid', request) == ['group:Readers']
