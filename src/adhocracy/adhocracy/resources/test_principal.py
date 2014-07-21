"""Tests for the principal package."""
import unittest
from mock import patch

from pyramid import testing


#############
#  helpers  #
#############

class DummyFolder(testing.DummyResource):

    def add(self, name, obj, **kwargs):
        self[name] = obj
        obj.__name__ = name
        obj.__parent__ = self
        obj.__oid__ = 1

    def check_name(self, name):
        if name == 'invalid':
            raise ValueError
        return name

    def next_name(self, obj, prefix=''):
        return prefix + '_0000000'


#############
#  Tests    #
#############

class PrincipalIntegrationTest(unittest.TestCase):

    def setUp(self):
        import substanced.principal
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.evolution')
        self.config.scan(substanced.principal)
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.principal')
        self.context = DummyFolder()

    def tearDown(self):
        testing.tearDown()

    def test_create_principals(self):
        from adhocracy.resources.principal import IPrincipalsPool
        from adhocracy.resources.principal import IUsersPool
        from adhocracy.resources.principal import IGroupsPool
        from adhocracy.resources.principal import IPasswordResetsPool

        inst = self.config.registry.content.create(
            IPrincipalsPool.__identifier__)

        assert IPrincipalsPool.providedBy(inst)
        assert 'users' in inst
        assert 'groups' in inst
        assert 'resets' in inst
        assert IUsersPool.providedBy(inst['users'])
        assert IGroupsPool.providedBy(inst['groups'])
        assert IPasswordResetsPool.providedBy(inst['resets'])

    def test_create_user(self):
        from adhocracy.resources.principal import IUser
        from adhocracy.resources.principal import User

        inst = self.config.registry.content.create(IUser.__identifier__)

        assert IUser.providedBy(inst)
        assert isinstance(inst, User)

    def test_create_and_add_user(self):
        from adhocracy.resources.principal import IPrincipalsPool
        from adhocracy.resources.principal import IUser
        from adhocracy.sheets.user import IPasswordAuthentication
        from adhocracy.sheets.user import IUserBasic

        self.config.include('adhocracy.sheets.user')

        principals_pool = self.config.registry.content.create(
            IPrincipalsPool.__identifier__)
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
        inst = self.config.registry.content.create(IUser.__identifier__,
                                                   parent=users_pool,
                                                   appstructs=appstructs)

        got_it = False
        for child in users_pool:
            if users_pool[child] == inst:
                got_it = True
                break
        assert got_it


class UserUnitTest(unittest.TestCase):

    def _makeOne(self):
        from adhocracy.resources.principal import User
        return User()

    def test_create(self):
        user = self._makeOne()
        assert user.email == ''
        assert user.password == ''
        assert user.tzname == 'UTC'


class UserLocatorAdapterUnitTest(unittest.TestCase):

    def _make_one(self, context=None, request=None):
        from adhocracy.resources.principal import UserLocatorAdapter
        return UserLocatorAdapter(context, request)

    def setUp(self):
        from substanced.interfaces import IFolder
        self.config = testing.setUp()
        context = testing.DummyResource(__provides__=IFolder)
        context['principals'] = testing.DummyResource(__is_service__=True,
                                                       __provides__=IFolder)
        context['principals']['users'] = testing.DummyResource()
        self.context = context

    def tearDown(self):
        testing.tearDown()

    def test_create(self):
        from substanced.interfaces import IUserLocator
        from zope.interface.verify import verifyObject
        inst = self._make_one()
        assert IUserLocator.providedBy(inst)
        assert verifyObject(IUserLocator, inst)

    def test_get_user_by_email_user_exists(self):
        user = testing.DummyResource(email='test@test.de')
        self.context['principals']['users']['User1'] = user
        inst = self._make_one(self.context, testing.DummyRequest())
        assert inst.get_user_by_email('test@test.de') is user

    def test_get_user_by_email_user_not_exists(self):
        user = testing.DummyResource(email='')
        self.context['principals']['users']['User1'] = user
        inst = self._make_one(self.context, testing.DummyRequest())
        assert inst.get_user_by_email('wrong@test.de') is None

    def test_get_user_by_login_user_exists(self):
        user = testing.DummyResource(name='login name')
        self.context['principals']['users']['User1'] = user
        inst = self._make_one(self.context, testing.DummyRequest())
        assert inst.get_user_by_login('login name') is user

    def test_get_user_by_login_user_not_exists(self):
        user = testing.DummyResource(name='')
        self.context['principals']['users']['User1'] = user
        inst = self._make_one(self.context, testing.DummyRequest())
        assert inst.get_user_by_login('wrong login name') is None


class UserLocatorAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.principal')
        self.context = testing.DummyResource()

    def tearDown(self):
        testing.tearDown()

    def test_create(self):
        from substanced.interfaces import IUserLocator
        from zope.component import getMultiAdapter
        assert getMultiAdapter((self.context, testing.DummyRequest), IUserLocator)
