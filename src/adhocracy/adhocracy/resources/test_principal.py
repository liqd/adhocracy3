"""Tests for the principal package."""
import unittest

from pyramid import testing


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


class PrincipalIntegrationTest(unittest.TestCase):

    def setUp(self):
        import substanced.principal
        import adhocracy.websockets.client as wsclient
        wsclient.disable()
        self.config = testing.setUp()
        self.config.include('substanced.content')
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


class UserUnitTest(unittest.TestCase):

    def _makeOne(self):
        from adhocracy.resources.principal import User
        return User()

    def test_create(self):
        user = self._makeOne()
        assert user.email == ''
        assert user.password == ''
        assert user.tzname == 'UTC'
