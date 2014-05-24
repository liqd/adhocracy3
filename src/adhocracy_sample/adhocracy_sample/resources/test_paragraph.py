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
        self.config.include('substanced.content')
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy_sample.resources.paragraph')
        context = DummyFolder()
        context.__graph__ = Graph(context)
        self.context = context


    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        from adhocracy_sample.resources.paragraph import IParagraphVersion
        from adhocracy_sample.resources.paragraph import IParagraph
        content_types = self.config.registry.content.factory_types
        assert IParagraph.__identifier__ in content_types
        assert IParagraphVersion.__identifier__ in content_types

    def test_includeme_registry_create_content(self):
        from adhocracy_sample.resources.paragraph import IParagraphVersion
        res = self.config.registry.content.create(IParagraphVersion.__identifier__,
                                                  self.context)
        assert IParagraphVersion.providedBy(res)
