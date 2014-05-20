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
    from adhocracy.resources.itemversion import itemversion_meta_defaults
    appstructs = {IVersionable.__identifier__: {'follows': follows}}
    return ResourceFactory(itemversion_meta_defaults)(parent=parent,
                                                      appstructs=appstructs)


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

    def next_name(self, subobject, prefix=''):
        return prefix + '_0000000'

###########
#  tests  #
###########


class ItemIntegrationTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        from adhocracy.resources.item import item_meta_defaults
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.item')
        self.config.include('adhocracy.resources.itemversion')
        self.config.include('adhocracy.resources.tag')
        self.config.include('adhocracy.sheets.name')
        self.config.include('adhocracy.sheets.tags')
        self.config.include('adhocracy.sheets.versions')
        self.config.include('adhocracy.subscriber')
        self.metadata = item_meta_defaults
        context = DummyFolder()
        context.__objectmap__ = ObjectMap(context)
        self.context = context

    def tearDown(self):
        testing.tearDown()

    def make_one(self):
        from adhocracy.resources import ResourceFactory
        return ResourceFactory(self.metadata)(parent=self.context)

    def test_create(self):
        from adhocracy.sheets.tags import ITag as ITagS
        from adhocracy.graph import get_references_for_isheet

        item = self.make_one()

        version0 = item['VERSION_0000000']
        assert IItemVersion.providedBy(version0)
        first_tag = item['FIRST']
        assert ITag.providedBy(first_tag)
        last_tag = item['LAST']
        assert ITag.providedBy(last_tag)
        first_targets = get_references_for_isheet(first_tag, ITagS)['elements']
        assert first_targets == [version0]
        last_targets = get_references_for_isheet(last_tag, ITagS)['elements']
        assert last_targets == [version0]

    def test_update_last_tag(self):
        """Test that LAST tag is updated correctly."""
        from adhocracy.graph import get_references_for_isheet
        from adhocracy.sheets.tags import ITag as ITagS
        item = self.make_one()
        version0 = item['VERSION_0000000']

        version1 = make_itemversion(parent=item, follows=[version0])

        first_tag = item['FIRST']
        first_targets = get_references_for_isheet(first_tag, ITagS)['elements']
        assert first_targets == [version0]
        last_tag = item['LAST']
        last_targets = get_references_for_isheet(last_tag, ITagS)['elements']
        assert last_targets == [version1]

    def test_update_last_tag_two_versions(self):
        """Test that if two versions are branched off the from the same
        version, both of them get the LAST tag.
        """
        from adhocracy.graph import get_references_for_isheet
        from adhocracy.sheets.tags import ITag as ITagS
        self.config.include('adhocracy.sheets.versions')
        self.config.include('adhocracy.subscriber')
        item = self.make_one()
        version0 = item['VERSION_0000000']

        version1 = make_itemversion(parent=item, follows=[version0])
        version2 = make_itemversion(parent=item, follows=[version0])

        first_tag = item['FIRST']
        first_targets = get_references_for_isheet(first_tag, ITagS)['elements']
        assert first_targets == [version0]
        last_tag = item['LAST']
        last_targets = get_references_for_isheet(last_tag, ITagS)['elements']
        assert last_targets == [version1, version2]


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.item')
        self.context = DummyFolder()

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        content_types = self.config.registry.content.factory_types
        assert IItem.__identifier__ in content_types

    def test_includeme_registry_create_content(self):
        res = self.config.registry.content.create(IItem.__identifier__,
                                                  parent=self.context,
                                                  run_after_creation=False)
        assert IItem.providedBy(res)
