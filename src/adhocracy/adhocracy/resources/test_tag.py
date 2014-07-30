import unittest

from pyramid import testing


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.testing import create_pool_with_graph
        config = testing.setUp()
        config.include('adhocracy.registry')
        config.include('adhocracy.events')
        config.include('adhocracy.sheets.metadata')
        config.include('adhocracy.resources.tag')
        self.config = config
        self.context = create_pool_with_graph()

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        from adhocracy.interfaces import ITag
        content_types = self.config.registry.content.factory_types
        assert ITag.__identifier__ in content_types

    def test_includeme_registry_create_content(self):
        from adhocracy.interfaces import ITag
        res = self.config.registry.content.create(ITag.__identifier__)
        assert ITag.providedBy(res)
