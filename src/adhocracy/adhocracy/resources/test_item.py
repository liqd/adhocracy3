import unittest

from pyramid import testing

from adhocracy.interfaces import IItem
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ITag


#############
#  helpers  #
#############

def make_itemversion(parent=None, follows=[]):
    from adhocracy.resources import ResourceFactory
    from adhocracy.sheets.versions import IVersionable
    from adhocracy.resources.itemversion import itemversion_metadata
    appstructs = {IVersionable.__identifier__: {'follows': follows}}
    return ResourceFactory(itemversion_metadata)(parent=parent,
                                                 appstructs=appstructs)


###########
#  tests  #
###########


class ItemIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.testing import create_folder_with_graph
        from adhocracy.resources.item import item_metadata
        config = testing.setUp()
        config.include('adhocracy.registry')
        config.include('adhocracy.events')
        config.include('adhocracy.sheets.metadata')
        config.include('adhocracy.sheets.versions')
        config.include('adhocracy.sheets.name')
        config.include('adhocracy.sheets.tags')
        config.include('adhocracy.resources.itemversion')
        config.include('adhocracy.resources.item')
        config.include('adhocracy.resources.tag')
        config.include('adhocracy.subscriber')
        self.config = config
        self.context = create_folder_with_graph()
        self.objectmap = self.context.__objectmap__
        self.graph = self.context.__graph__
        self.metadata = item_metadata

    def tearDown(self):
        testing.tearDown()

    def make_one(self, name='name'):
        from adhocracy.sheets.name import IName
        from adhocracy.resources import ResourceFactory
        appstructs = {IName.__identifier__: {'name': name}}
        inst = ResourceFactory(self.metadata)(parent=self.context,
                                              appstructs=appstructs)
        return inst

    def test_create(self):
        from adhocracy.sheets.tags import ITag as ITagS

        item = self.make_one()

        version0 = item['VERSION_0000000']
        assert IItemVersion.providedBy(version0)
        first_tag = item['FIRST']
        assert ITag.providedBy(first_tag)
        last_tag = item['LAST']
        assert ITag.providedBy(last_tag)
        first_targets = self.graph.get_references_for_isheet(first_tag, ITagS)['elements']
        assert first_targets == [version0]
        last_targets = self.graph.get_references_for_isheet(last_tag, ITagS)['elements']
        assert last_targets == [version0]

    def test_update_last_tag(self):
        """Test that LAST tag is updated correctly."""
        from adhocracy.sheets.tags import ITag as ITagS
        item = self.make_one()
        version0 = item['VERSION_0000000']

        version1 = make_itemversion(parent=item, follows=[version0])

        last_tag = item['LAST']
        last_targets = self.graph.get_references_for_isheet(last_tag, ITagS)['elements']
        assert last_targets == [version1]

    def test_update_last_tag_two_versions(self):
        """Test that if two versions are branched off the from the same
        version, both of them get the LAST tag.
        """
        from adhocracy.sheets.tags import ITag as ITagS
        self.config.include('adhocracy.sheets.versions')
        self.config.include('adhocracy.subscriber')
        item = self.make_one()
        version0 = item['VERSION_0000000']

        version1 = make_itemversion(parent=item, follows=[version0])
        version2 = make_itemversion(parent=item, follows=[version0])

        last_tag = item['LAST']
        last_targets = self.graph.get_references_for_isheet(last_tag, ITagS)['elements']
        assert last_targets == [version1, version2]


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.testing import create_folder_with_graph
        from adhocracy.resources.item import item_metadata
        config = testing.setUp()
        config.include('adhocracy.registry')
        config.include('adhocracy.events')
        config.include('adhocracy.resources.item')
        config.include('adhocracy.sheets.metadata')
        self.config = config
        self.context = create_folder_with_graph()
        self.metyyadata = item_metadata

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        content_types = self.config.registry.content.factory_types
        assert IItem.__identifier__ in content_types

    def test_includeme_registry_create_content(self):
        res = self.config.registry.content.create(IItem.__identifier__,
                                                  run_after_creation=False)
        assert IItem.providedBy(res)
