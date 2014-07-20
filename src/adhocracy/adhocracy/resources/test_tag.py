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


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.tag')
        self.context = DummyFolder()

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
