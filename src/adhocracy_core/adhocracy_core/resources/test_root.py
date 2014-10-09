import unittest

from pyramid import testing


class RootPoolIntegrationTest(unittest.TestCase):

    def setUp(self):
        config = testing.setUp()
        config.include('adhocracy_core.registry')
        config.include('adhocracy_core.events')
        config.include('adhocracy_core.catalog')
        config.include('adhocracy_core.graph')
        config.include('adhocracy_core.resources.root')
        config.include('adhocracy_core.resources.pool')
        config.include('adhocracy_core.resources.principal')
        config.include('adhocracy_core.sheets')
        config.include('adhocracy_core.messaging')
        self.config = config
        self.context = testing.DummyResource()
        request = testing.DummyRequest()
        request.registry = config.registry
        self.request = request
        self.registry = config.registry

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        from adhocracy_core.resources.root import IRootPool
        content_types = self.config.registry.content.factory_types
        assert IRootPool.__identifier__ in content_types

    def test_includeme_registry_register_meta(self):
        from adhocracy_core.resources.root import IRootPool
        meta = self.config.registry.content.meta
        assert IRootPool.__identifier__ in meta

    def test_includeme_registry_create_content_with_default_platform_id(self):
        from adhocracy_core.resources.root import IRootPool
        from adhocracy_core.interfaces import IPool
        from adhocracy_core.utils import find_graph
        from substanced.util import find_objectmap
        from substanced.util import find_catalog
        from substanced.util import find_service
        inst = self.config.registry.content.create(IRootPool.__identifier__)
        assert IRootPool.providedBy(inst)
        assert IPool.providedBy(inst['adhocracy'])
        assert find_objectmap(inst) is not None
        assert find_graph(inst) is not None
        assert find_graph(inst)._objectmap is not None
        assert find_catalog(inst, 'system') is not None
        assert find_catalog(inst, 'adhocracy') is not None
        assert find_service(inst, 'principals', 'users') is not None

    def test_includeme_registry_create_content_with_custom_platform_id(self):
        from adhocracy_core.resources.root import IRootPool
        from adhocracy_core.interfaces import IPool
        self.config.registry.settings['adhocracy.platform_id'] = 'platform'
        inst = self.config.registry.content.create(IRootPool.__identifier__)
        assert IPool.providedBy(inst['platform'])

    def test_includeme_registry_add_acl(self):
        from adhocracy_core.resources.root import IRootPool
        from substanced.util import get_acl
        from pyramid.security import ALL_PERMISSIONS
        from pyramid.security import Allow
        inst = self.config.registry.content.create(IRootPool.__identifier__)
        assert get_acl(inst) == [(Allow, 'system.Everyone', 'view'),
                                 (Allow, 'system.Everyone', 'add_user'),
                                 (Allow, 'system.Everyone', 'create_sheet_password'),
                                 (Allow, 'system.Everyone', 'create_sheet_userbasic'),
                                 (Allow, 'role:god', ALL_PERMISSIONS),
                                 ]

    def test_includeme_registry_add_initial_god_user(self):
        from substanced.interfaces import IUserLocator
        from adhocracy_core.resources.root import IRootPool
        inst = self.config.registry.content.create(IRootPool.__identifier__)
        locator = self.registry.getMultiAdapter((inst, self.request),
                                                IUserLocator)
        user_god = locator.get_user_by_login('god')
        assert not user_god is None
        assert user_god.password != ''
        assert user_god.email == 'sysadmin@test.de'

    def test_includeme_registry_add_initial_god_user_with_custom_login(self):
        from substanced.interfaces import IUserLocator
        from adhocracy_core.resources.root import IRootPool
        self.config.registry.settings['adhocracy.initial_login'] = 'custom'
        self.config.registry.settings['adhocracy.initial_password'] = 'password'
        self.config.registry.settings['adhocracy.initial_email'] = 'c@test.de'
        inst = self.config.registry.content.create(IRootPool.__identifier__)
        locator = self.registry.getMultiAdapter((inst, self.request),
                                                IUserLocator)
        user_god = locator.get_user_by_login('custom')
        assert not user_god is None
        assert user_god.password != ''
        assert user_god.email == 'c@test.de'

    def test_includeme_registry_add_initial_god_group(self):
        from adhocracy_core.resources.root import IRootPool
        from adhocracy_core.interfaces import IGroupLocator
        from adhocracy_core.sheets.principal import IGroup
        from adhocracy_core.utils import get_sheet
        inst = self.config.registry.content.create(IRootPool.__identifier__)
        locator = self.registry.getMultiAdapter((inst, self.request),
                                                IGroupLocator)
        group_gods = locator.get_group_by_id('gods')
        group_sheet = get_sheet(group_gods, IGroup)
        group_users = [x.__name__ for x in group_sheet.get()['users']]
        group_roles = group_sheet.get()['roles']
        assert not group_gods is None
        assert group_users == ['0000000']
        assert group_roles == ['god']


