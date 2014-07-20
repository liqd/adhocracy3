from pyramid import testing

import unittest


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
        from adhocracy.graph import Graph
        self.config = testing.setUp()
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy_sample.resources.section')
        context = DummyFolder()
        context.__graph__ = Graph(context)
        self.context = context



    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        from adhocracy_sample.resources.section import ISectionVersion
        from adhocracy_sample.resources.section import ISection
        content_types = self.config.registry.content.factory_types
        assert ISection.__identifier__ in content_types
        assert ISectionVersion.__identifier__ in content_types

    def test_includeme_registry_create_content(self):
        from adhocracy_sample.resources.section import ISectionVersion
        res = self.config.registry.content.create(ISectionVersion.__identifier__,
                                                  self.context)
        assert ISectionVersion.providedBy(res)
