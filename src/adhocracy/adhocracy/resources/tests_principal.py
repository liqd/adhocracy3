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


class PrincipalsIntegrationTest(unittest.TestCase):

    def setUp(self):
        import substanced.principal
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.scan(substanced.principal)
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.principal')
        self.context = DummyFolder()

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_create_content(self):
        from adhocracy.resources.principal import IPrincipalsPool
        from adhocracy.resources.principal import IUsersPool
        from adhocracy.resources.principal import IGroupsPool
        from adhocracy.resources.principal import IPasswordResetsPool

        principals = self.config.registry.content.create(
            IPrincipalsPool.__identifier__, self.context)

        assert IPrincipalsPool.providedBy(principals)
        assert 'users' in principals
        assert 'groups' in principals
        assert 'resets' in principals
        assert IUsersPool.providedBy(principals['users'])
        assert IGroupsPool.providedBy(principals['groups'])
        assert IPasswordResetsPool.providedBy(principals['resets'])


class PrincipalslUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self):
        from adhocracy.resources.principal import PrincipalsPool
        return PrincipalsPool()
