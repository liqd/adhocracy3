import unittest

from pyramid import testing
import pytest

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource



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

    def next_name(self, obj, prefix=''):
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
        from adhocracy.interfaces import IItemVersion
        from adhocracy.interfaces import ITag

        inst = self.make_one()

        item_version = inst['VERSION_0000000']
        first = inst['FIRST']
        last = inst['LAST']
        assert IItemVersion.providedBy(item_version)
        assert ITag.providedBy(first)
        assert ITag.providedBy(last)
        wanted = {'adhocracy.sheets.tags.ITag': {'elements':
                                                 [item_version]},
                  'adhocracy.sheets.name.IName': {'name': 'FIRST'}}
        assert first._propertysheets == wanted
        wanted = {'adhocracy.sheets.tags.ITag': {'elements':
                                                 [item_version]},
                  'adhocracy.sheets.name.IName': {'name': 'LAST'}}
        assert last._propertysheets == wanted

    def test_update_last_tag(self):
        """Test that LAST tag is updated correctly."""
        # Create item with auto-created first version
        item = self.make_one()
        item_version = item['VERSION_0000000']

        # Create another version
        new_version = make_itemversion(parent=item, follows=[item_version])

        # FIRST should still point to the old version
        wanted = {'adhocracy.sheets.tags.ITag': {'elements':
                                                 [item_version]},
                  'adhocracy.sheets.name.IName': {'name': 'FIRST'}}
        assert item['FIRST']._propertysheets == wanted
        # LAST tag should point to new version,
        wanted = {'adhocracy.sheets.tags.ITag': {'elements':
                                                 [new_version]},
                  'adhocracy.sheets.name.IName': {'name': 'LAST'}}
        assert item['LAST']._propertysheets == wanted

    def test_update_last_tag_two_versions(self):
        """Test that if two versions are branched off the from the same
        version, both of them get the LAST tag.

        """
        self.config.include('adhocracy.sheets.versions')
        self.config.include('adhocracy.subscriber')

        # Create item with auto-created first version
        item = self.make_one()
        item_version = item['VERSION_0000000']

        # Create two other versions, but pointing to the same predecessor
        new_version1 = make_itemversion(parent=item, follows=[item_version])
        new_version2 = make_itemversion(parent=item, follows=[item_version])

        # first tag should point to the old version
        wanted = {'adhocracy.sheets.tags.ITag': {'elements':
                                                 [item_version]},
                  'adhocracy.sheets.name.IName': {'name': 'FIRST'}}
        assert item['FIRST']._propertysheets == wanted
        # LAST tag should point to both new versions
        wanted = {'adhocracy.sheets.tags.ITag': {'elements':
                                                 [new_version1,
                                                  new_version2]},
                  'adhocracy.sheets.name.IName': {'name': 'LAST'}}
        assert item['LAST']._propertysheets == wanted


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
        from adhocracy.interfaces import IItem
        content_types = self.config.registry.content.factory_types
        assert IItem.__identifier__ in content_types

    def test_includeme_registry_create_content(self):
        from adhocracy.interfaces import IItem
        res = self.config.registry.content.create(IItem.__identifier__,
                                                  parent=self.context,
                                                  run_after_creation=False)
        assert IItem.providedBy(res)
