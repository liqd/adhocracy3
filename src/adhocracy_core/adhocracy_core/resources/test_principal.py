"""Tests for the principal package."""
import unittest

from pyramid import testing
from pytest import fixture
from pytest import mark


class PrincipalIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy_core.testing import create_pool_with_graph
        config = testing.setUp()
        config.include('pyramid_mailer.testing')
        config.include('pyramid_mako')
        config.include('adhocracy_core.registry')
        config.include('adhocracy_core.events')
        config.include('adhocracy_core.messaging')
        config.include('adhocracy_core.sheets.metadata')
        config.include('adhocracy_core.sheets.name')
        config.include('adhocracy_core.sheets.principal')
        config.include('adhocracy_core.resources.principal')
        self.config = config
        self.context = create_pool_with_graph()

    def tearDown(self):
        testing.tearDown()

    def test_create_principals(self):
        from adhocracy_core.resources.principal import IPrincipalsService
        from adhocracy_core.resources.principal import IUsersService
        from adhocracy_core.resources.principal import IGroupsService
        from adhocracy_core.resources.principal import IPasswordResetsService

        inst = self.config.registry.content.create(
            IPrincipalsService.__identifier__, parent=self.context)

        assert IPrincipalsService.providedBy(inst)
        assert 'users' in inst
        assert 'groups' in inst
        assert 'resets' in inst
        assert IUsersService.providedBy(inst['users'])
        assert IGroupsService.providedBy(inst['groups'])
        assert IPasswordResetsService.providedBy(inst['resets'])

    def test_register_services(self):
        from adhocracy_core.resources.principal import IPrincipalsService

        self.config.registry.content.create(IPrincipalsService.__identifier__,
                                            parent=self.context)

        from substanced.util import find_service
        assert find_service(self.context, 'principals', 'users')
        assert find_service(self.context, 'principals', 'groups')
        assert find_service(self.context, 'principals', 'resets')

    def test_create_user(self):
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import User

        inst = self.config.registry.content.create(IUser.__identifier__)

        assert IUser.providedBy(inst)
        assert isinstance(inst, User)

    def test_create_and_add_user(self):
        from adhocracy_core.resources.principal import IPrincipalsService
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.sheets.principal import IPasswordAuthentication
        from adhocracy_core.sheets.principal import IUserBasic

        self.config.include('adhocracy_core.sheets.principal')

        principals_pool = self.config.registry.content.create(
            IPrincipalsService.__identifier__)
        users_pool = principals_pool['users']
        appstructs = {
            IUserBasic.__identifier__ : {
                'name': 'Anna Müller',
                'email': 'anna@example.org'
            },
            IPasswordAuthentication.__identifier__ : {
                'password': 'fodThyd2'
            },
        }
        user = self.config.registry.content.create(IUser.__identifier__,
                                                   parent=users_pool,
                                                   appstructs=appstructs)
        assert users_pool['0000000'] is user

    def test_create_group(self):
        from adhocracy_core.resources.principal import IGroup
        inst = self.config.registry.content.create(IGroup.__identifier__)
        assert IGroup.providedBy(inst)

    def test_create_and_add_group(self):
        from adhocracy_core.utils import get_sheet
        from adhocracy_core.resources.principal import IPrincipalsService
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import IGroup
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.sheets.name import IName
        import adhocracy_core.sheets.principal

        self.config.include('adhocracy_core.sheets.principal')

        principals_pool = self.config.registry.content.create(
            IPrincipalsService.__identifier__,
            parent=self.context)
        groups_pool = principals_pool['groups']
        appstructs = {IName.__identifier__: {'name': 'Group1'},
                      adhocracy_core.sheets.principal.IGroup.__identifier__:
                          {'roles': ['reader']}}
        group = self.config.registry.content.create(IGroup.__identifier__,
                                                    parent=groups_pool,
                                                    appstructs=appstructs)
        users_pool = principals_pool['users']
        appstructs = {IPermissions.__identifier__: {'groups': [group]}}
        user = self.config.registry.content.create(IUser.__identifier__,
                                                   parent=users_pool,
                                                   appstructs=appstructs)
        group_sheet = get_sheet(group, adhocracy_core.sheets.principal.IGroup)
        assert groups_pool['Group1'] is group
        assert group_sheet.get()['users'] == [user]
        assert group_sheet.get()['roles'] == ['reader']


class UserMetaUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy_core.resources.principal import user_metadata
        return user_metadata

    def test_meta(self):
        from adhocracy_core.resources.principal import IUser
        import adhocracy_core.sheets
        meta = self._make_one()
        assert meta.iresource is IUser
        assert meta.permission_add == 'add_user'
        assert meta.is_implicit_addable is False
        assert meta.basic_sheets ==\
            [adhocracy_core.sheets.principal.IUserBasic,
             adhocracy_core.sheets.principal.IPermissions,
             adhocracy_core.sheets.metadata.IMetadata,
             adhocracy_core.sheets.pool.IPool,
             ]
        assert meta.extended_sheets ==\
               [adhocracy_core.sheets.principal.IPasswordAuthentication,
                adhocracy_core.sheets.rate.ICanRate,
               ]


class UserUnitTest(unittest.TestCase):

    def _makeOne(self):
        from adhocracy_core.resources.principal import User
        return User()

    def test_create(self):
        user = self._makeOne()
        assert user.email == ''
        assert user.password == ''
        assert user.tzname == 'UTC'


class TestUserLocatorAdapter:

    def _make_one(self, context=None, request=None):
        from adhocracy_core.resources.principal import UserLocatorAdapter
        return UserLocatorAdapter(context, request)

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
        inst = self._make_one()
        assert IRolesUserLocator.providedBy(inst)
        assert verifyObject(IRolesUserLocator, inst)

    def test_get_user_by_email_user_exists(self, context, request):
        user = testing.DummyResource(email='test@test.de')
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_user_by_email('test@test.de') is user

    def test_get_user_by_email_user_not_exists(self, context, request):
        user = testing.DummyResource(email='')
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_user_by_email('wrong@test.de') is None

    def test_get_user_by_login_user_exists(self, context, request):
        user = testing.DummyResource(name='login name')
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_user_by_login('login name') is user

    def test_get_user_by_login_user_not_exists(self, context, request):
        user = testing.DummyResource(name='')
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_user_by_login('wrong login name') is None

    def test_get_user_by_activation_path_user_exists(self, context, request):
        user = testing.DummyResource(activation_path='/activate/foo')
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_user_by_activation_path('/activate/foo') is user
        
    def test_get_user_by_activation_path_user_not_exists(self, context, request):
        user = testing.DummyResource(activation_path=None)
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_user_by_activation_path('/activate/no_such_link') is None

    def test_get_user_by_userid_user_exists(self, context, request):
        user = testing.DummyResource()
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_user_by_userid('/principals/users/User1') is user

    def test_get_user_by_userid_user_not_exists(self, context, request):
        inst = self._make_one(context, request)
        assert inst.get_user_by_userid('/principals/users/User1') is None

    def test_get_groupids_user_exists(self, context, mock_sheet, request):
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.testing import add_and_register_sheet
        group = testing.DummyResource(__name__='group1')
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        mock_sheet.get.return_value = {'groups': [group]}
        user = testing.DummyResource()
        add_and_register_sheet(user, mock_sheet, request.registry)
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_groupids('/principals/users/User1') == ['group:group1']

    def test_get_groupids_user_not_exists(self, context, request):
        inst = self._make_one(context, request)
        assert inst.get_groupids('/principals/users/User1') is None

    def test_get_roleids_user_exists(self, context, mock_sheet, request):
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.testing import add_and_register_sheet
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        mock_sheet.get.return_value = {'roles': ['role1']}
        user = testing.DummyResource()
        add_and_register_sheet(user, mock_sheet, request.registry)
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_roleids('/principals/users/User1') == ['role:role1']

    def test_get_roleids_user_not_exists(self, context, request):
        inst = self._make_one(context, request)
        assert inst.get_roleids('/principals/users/User1') is None


class UserLocatorAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy_core.registry')
        self.config.include('adhocracy_core.resources.principal')
        self.context = testing.DummyResource()
        self.registry = self.config.registry

    def tearDown(self):
        testing.tearDown()

    def test_create(self):
        from adhocracy_core.interfaces import IRolesUserLocator
        assert self.registry.getMultiAdapter(
            (self.context,  testing.DummyRequest), IRolesUserLocator)


class TestGroupLocatorAdapter:

    @fixture
    def context(self, pool, service):
        pool['principals'] = service 
        pool['principals']['groups'] = service.clone()
        return pool
    
    @fixture
    def request(self, registry):
        request = testing.DummyRequest()
        request.registry = registry
        return request

    @fixture
    def inst(self, context, request):
        from adhocracy_core.resources.principal import GroupLocatorAdapter
        return GroupLocatorAdapter(context, request)

    def test_create(self, inst):
        from adhocracy_core.interfaces import IGroupLocator
        from zope.interface.verify import verifyObject
        assert IGroupLocator.providedBy(inst)
        assert verifyObject(IGroupLocator, inst)

    def test_get_roleids_group_exists_no_roles(self, inst, context, mock_sheet, registry):
        from adhocracy_core.sheets.principal import IGroup
        from adhocracy_core.testing import add_and_register_sheet
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IGroup)
        mock_sheet.get.return_value = {'roles': []}
        group = testing.DummyResource()
        context['principals']['groups']['Group1'] = group
        add_and_register_sheet(group, mock_sheet, registry)
        assert inst.get_roleids('Group1') == []

    def test_get_roleids_group_exists_roles(self, inst, context, mock_sheet, registry):
        from adhocracy_core.sheets.principal import IGroup
        from adhocracy_core.testing import add_and_register_sheet
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IGroup)
        mock_sheet.get.return_value = {'roles': ['role1']}
        group = testing.DummyResource()
        context['principals']['groups']['Group1'] = group
        add_and_register_sheet(group, mock_sheet, registry)
        assert inst.get_roleids('Group1') == ['role:role1']

    def test_get_roleids_by_id_group_not_exists(self, inst):
        assert inst.get_roleids('Group1') is None

    def test_get_group_by_id_with_prefix_group_exists(self, inst, context):
        group = testing.DummyResource()
        context['principals']['groups']['Group1'] = group
        assert inst.get_group_by_id('group:Group1') is group

    def test_get_group_by_id_without_prefix_group_exists(self, inst, context):
        group = testing.DummyResource()
        context['principals']['groups']['Group1'] = group
        assert inst.get_group_by_id('Group1') is group

    def test_get_group_by_id_group_not_exists(self, inst):
        assert inst.get_group_by_id('Group1') is None


class TestGroupsAndRolesFinder:

    @fixture
    def request(self, context, registry):
        request = testing.DummyRequest(context=context)
        request.registry = registry
        return request

    def _call_fut(self, userid, request):
        from adhocracy_core.resources.principal import groups_and_roles_finder
        return groups_and_roles_finder(userid, request)

    def test_userid_wrong(self, request, mock_group_locator, mock_user_locator):
        assert self._call_fut('WRONG', request) == []
        assert mock_user_locator.get_groupids.call_args[0] == ('WRONG',)
        assert mock_user_locator.get_roleids.call_args[0] == ('WRONG',)

    def test_userid_with_roles(self, request, mock_group_locator,
                               mock_user_locator):
        mock_user_locator.get_roleids.return_value = ['role:reader']
        assert self._call_fut('userid', request) == ['role:reader']

    def test_userid_with_groups(self, request, mock_group_locator,
                                mock_user_locator):
        mock_user_locator.get_groupids.return_value = ['group:Readers']
        assert self._call_fut('userid', request) == ['group:Readers']

    def test_userid_with_groups_roles(self, request, mock_group_locator,
                                      mock_user_locator):
        mock_user_locator.get_groupids.return_value = ['group:Readers']
        mock_group_locator.get_roleids.return_value = ['role:reader']
        self._call_fut('userid', request) == ['group:Readers', 'role:reader']
        assert mock_group_locator.get_roleids.call_args[0] == ('group:Readers',)
        

class TestIntegrationSendRegistrationMail():

    @fixture
    def integration(self, config):
        config.include('pyramid_mailer.testing')
        config.include('pyramid_mako')
        config.include('adhocracy_core.registry')
        config.include('adhocracy_core.messaging')

    @mark.usefixtures('integration')
    def test_send_registration_mail(self, registry):
        from adhocracy_core.resources.principal import User
        from adhocracy_core.resources.principal import send_registration_mail
        mailer = registry.messenger._get_mailer()
        assert len(mailer.outbox) == 0
        user = User()
        user.name = 'Anna Müller'
        user.email = 'anna@example.org'
        send_registration_mail(context=user, registry=registry)
        assert user.activation_path.startswith('/activate/')
        assert len(mailer.outbox) == 1
        msg = mailer.outbox[0]
        # The DummyMailer is too stupid to use a default sender, hence we add
        # one manually
        msg.sender = 'support@unconfigured.domain'
        msgtext = str(msg.to_message())
        assert user.activation_path in msgtext
