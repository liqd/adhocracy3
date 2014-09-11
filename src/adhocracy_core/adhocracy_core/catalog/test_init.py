import unittest

from pyramid import testing


class InlcudemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy_core.catalog')

    def tearDown(self):
        testing.tearDown()

    def test_add_indexing_adapter(self):
        from substanced.interfaces import IIndexingActionProcessor
        assert IIndexingActionProcessor(object()) is not None

    def test_add_directives(self):
        assert 'add_catalog_factory' in self.config.registry._directives
        assert 'add_indexview' in self.config.registry._directives
