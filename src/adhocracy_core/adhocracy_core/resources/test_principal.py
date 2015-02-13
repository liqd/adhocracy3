"""Tests for the principal package."""
import unittest
from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


from pytest import mark
from pytest import fixture


def test_principals_meta():
    from .principal import principals_metadata
    from .principal import IPrincipalsService
    meta = principals_metadata
    assert meta.iresource is IPrincipalsService
    assert meta.permission_add == 'add_service'
    assert meta.content_name == 'principals'


def test_users_meta():
    from .principal import users_metadata
    from .principal import IUsersService
    meta = users_metadata
    assert meta.iresource is IUsersService
    assert meta.permission_add == 'add_service'
    assert meta.content_name == 'users'


def test_groups_meta():
    from .principal import groups_metadata
    from .principal import IGroupsService
    meta = groups_metadata
    assert meta.iresource is IGroupsService
    assert meta.permission_add == 'add_service'
    assert meta.content_name == 'groups'


def test_user_meta():
    from .principal import user_metadata
    from .principal import IUser
    from .principal import send_registration_mail
    from .principal import User
    import adhocracy_core.sheets
    meta = user_metadata
    assert meta.iresource is IUser
    assert meta.content_class == User  # FIXME remove ths special class
    assert meta.permission_add == 'add_user'
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
    assert send_registration_mail in meta.after_creation


def test_group_meta():
    from .principal import group_metadata
    from .principal import IGroup
    from .principal import Group
    meta = group_metadata
    assert meta.iresource is IGroup
    assert meta.content_class == Group
    assert meta.permission_add == 'add_group'
    assert meta.is_implicit_addable is False
    assert meta.element_types == []


@fixture
def integration(config):
    config.include('pyramid_mailer.testing')
    config.include('pyramid_mako')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.registry')
    config.include('adhocracy_core.messaging')
    config.include('adhocracy_core.sheets.metadata')
    config.include('adhocracy_core.sheets.name')
    config.include('adhocracy_core.sheets.principal')
    config.include('adhocracy_core.resources.principal')
    config.include('adhocracy_core.resources.subscriber')


@mark.usefixtures('integration')
class TestPrincipalsService:

    @fixture
    def context(self, pool):
        return pool

    def test_create_principals(self, context, config, registry):
        from adhocracy_core.resources.principal import IPrincipalsService
        from adhocracy_core.resources.principal import IUsersService
        from adhocracy_core.resources.principal import IGroupsService
        from adhocracy_core.resources.principal import IPasswordResetsService

        inst = registry.content.create(
            IPrincipalsService.__identifier__, parent=context)

        assert IPrincipalsService.providedBy(inst)
        assert 'users' in inst
        assert 'groups' in inst
        assert 'resets' in inst
        assert IUsersService.providedBy(inst['users'])
        assert IGroupsService.providedBy(inst['groups'])
        assert IPasswordResetsService.providedBy(inst['resets'])

    def test_register_services(self, context, registry):
        from adhocracy_core.resources.principal import IPrincipalsService

        registry.content.create(IPrincipalsService.__identifier__,
                                            parent=context)

        from substanced.util import find_service
        assert find_service(context, 'principals', 'users')
        assert find_service(context, 'principals', 'groups')
        assert find_service(context, 'principals', 'resets')

    def test_create_user(self, registry):
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import User

        inst = registry.content.create(IUser.__identifier__)

        assert IUser.providedBy(inst)
        assert isinstance(inst, User)

    def test_create_and_add_user(self, registry):
        from adhocracy_core.resources.principal import IPrincipalsService
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.sheets.principal import IPasswordAuthentication
        from adhocracy_core.sheets.principal import IUserBasic

        principals_pool = registry.content.create(
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
        user = registry.content.create(IUser.__identifier__,
                                                   parent=users_pool,
                                                   appstructs=appstructs)
        assert users_pool['0000000'] is user

    def test_create_group(self, registry):
        from adhocracy_core.resources.principal import IGroup
        inst = registry.content.create(IGroup.__identifier__)
        assert IGroup.providedBy(inst)

    def test_create_and_add_group(self, pool_graph, registry):
        from adhocracy_core.utils import get_sheet
        from adhocracy_core.resources.principal import IPrincipalsService
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import IGroup
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.sheets.name import IName
        import adhocracy_core.sheets.principal
        context = pool_graph

        principals_pool = registry.content.create(
            IPrincipalsService.__identifier__,
            parent=context)
        groups_pool = principals_pool['groups']
        appstructs = {IName.__identifier__: {'name': 'Group1'},
                      adhocracy_core.sheets.principal.IGroup.__identifier__:
                           {'roles': ['reader']}}
        group = registry.content.create(IGroup.__identifier__,
                                        parent=groups_pool,
                                        appstructs=appstructs)
        users_pool = principals_pool['users']
        appstructs = {IPermissions.__identifier__: {'groups': [group]}}
        user = registry.content.create(IUser.__identifier__,
                                       parent=users_pool,
                                       appstructs=appstructs)
        group_sheet = get_sheet(group, adhocracy_core.sheets.principal.IGroup)
        assert groups_pool['Group1'] is group
        assert group_sheet.get()['users'] == [user]
        assert group_sheet.get()['roles'] == ['reader']


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

    def test_get_role_and_group_role_ids_user_exists(self, context, request):
        inst = self._make_one(context, request)
        inst.get_user_by_userid = Mock()
        inst.get_user_by_userid.return_value = context
        inst.get_roleids = Mock()
        inst.get_roleids.return_value = ['role:admin']
        inst.get_group_roleids = Mock()
        inst.get_group_roleids.return_value = ['role:reader']
        assert inst.get_role_and_group_roleids('/principals/users/User1') ==\
               ['role:admin', 'role:reader']

    def test_get_role_and_group_roleids_user_not_exists(self, context, request):
        inst = self._make_one(context, request)
        assert inst.get_role_and_group_roleids('/principals/users/User1') is None

    def test_get_group_roleids_user_exists(self, context, mock_sheet, request):
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.testing import add_and_register_sheet
        group = testing.DummyResource(__name__='group1', roles=[])
        user = testing.DummyResource()
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        mock_sheet.get.return_value = {'groups': [group]}
        add_and_register_sheet(user, mock_sheet, request.registry)
        group.roles = ['role1']
        context['principals']['users']['User1'] = user
        inst = self._make_one(context, request)
        assert inst.get_group_roleids('/principals/users/User1') == ['role:role1']

    def test_get_group_roleids_user_not_exists(self, context, request):
        inst = self._make_one(context, request)
        assert inst.get_group_roleids('/principals/users/User1') is None

    def test_get_roleids_user_exists(self, context, mock_sheet, request):
        from adhocracy_core.testing import add_and_register_sheet
        user = testing.DummyResource(roles=['role1'])
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


class TestGroupsAndRolesFinder:

    @fixture
    def request(self, context, registry):
        request = testing.DummyRequest(context=context)
        request.registry = registry
        return request

    def _call_fut(self, userid, request):
        from adhocracy_core.resources.principal import groups_and_roles_finder
        return groups_and_roles_finder(userid, request)

    def test_userid_wrong(self, request,  mock_user_locator):
        assert self._call_fut('WRONG', request) == []
        assert mock_user_locator.get_groupids.call_args[0] == ('WRONG',)
        assert mock_user_locator.get_role_and_group_roleids.call_args[0] == ('WRONG',)

    def test_userid_with_roles(self, request, mock_user_locator):
        mock_user_locator.get_role_and_group_roleids.return_value = ['role:reader']
        assert self._call_fut('userid', request) == ['role:reader']

    def test_userid_with_groups_and_group_roles(self, request, mock_user_locator):
        mock_user_locator.get_role_and_group_roleids.return_value = ['group:Readers']
        assert self._call_fut('userid', request) == ['group:Readers']


class TestIntegrationSendRegistrationMail:

    @fixture
    def sample_user(self):
        from zope.interface import directlyProvides
        from adhocracy_core.resources.principal import User
        from adhocracy_core.sheets.metadata import IMetadata
        user = User()
        user.name = 'Anna Müller'
        user.email = 'anna@example.org'
        directlyProvides(user, IMetadata)
        return user

    @mark.usefixtures('integration')
    def test_send_registration_mail_successfully(self, registry, sample_user):
        from adhocracy_core.resources.principal import send_registration_mail
        mailer = registry.messenger._get_mailer()
        assert len(mailer.outbox) == 0
        send_registration_mail(context=sample_user, registry=registry)
        assert sample_user.activation_path.startswith('/activate/')
        assert len(mailer.outbox) == 1
        msg = mailer.outbox[0]
        # The DummyMailer is too stupid to use a default sender, hence we add
        # one manually
        msg.sender = 'support@unconfigured.domain'
        msgtext = str(msg.to_message())
        assert sample_user.activation_path in msgtext

    @mark.usefixtures('integration')
    def test_send_registration_mail_smtp_error(self, registry, sample_user):
        from colander import Invalid
        from smtplib import SMTPException
        from adhocracy_core.messaging import Messenger
        from adhocracy_core.resources.principal import send_registration_mail
        mock_messenger = Mock(spec=Messenger)
        mock_messenger.render_and_send_mail = Mock(
            side_effect=SMTPException('bad luck'))
        registry.messenger = mock_messenger
        with raises(Invalid) as err_info:
            send_registration_mail(context=sample_user, registry=registry)
        assert 'Cannot send' in err_info.exconly()
        assert 'bad luck' in err_info.exconly()

    @mark.usefixtures('integration')
    def test_send_registration_mail_skip(self, registry, sample_user):
        from adhocracy_core.resources.principal import send_registration_mail
        registry.settings['adhocracy.skip_registration_mail'] = 'true'
        send_registration_mail(context=sample_user, registry=registry)
        assert sample_user.active is True
        assert sample_user.activation_path is None
