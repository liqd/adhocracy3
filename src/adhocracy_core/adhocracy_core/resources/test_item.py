import unittest

from pyramid import testing
from pytest import raises
from pytest import fixture
from pytest import mark
import colander

from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import ITag


def test_item_meta():
    from .item import item_meta
    from .item import create_initial_content_for_item
    from .item import IItem
    from .item import IItemVersion
    import adhocracy_core.sheets
    meta = item_meta
    assert meta.iresource == IItem
    assert meta.basic_sheets == (adhocracy_core.sheets.tags.ITags,
                                 adhocracy_core.sheets.versions.IVersions,
                                 adhocracy_core.sheets.pool.IPool,
                                 adhocracy_core.sheets.metadata.IMetadata,
                                 adhocracy_core.sheets.workflow.IWorkflowAssignment,
                                 )
    assert meta.element_types == (
        IItemVersion,
        ITag
    )
    assert create_initial_content_for_item in meta.after_creation
    assert meta.item_type == IItemVersion
    assert meta.permission_create == 'create_item'
    assert meta.use_autonaming
    assert meta.autonaming_prefix == 'item_'


def make_itemversion(parent=None, follows=[]):
    from adhocracy_core.resources import ResourceFactory
    from adhocracy_core.sheets.versions import IVersionable
    from adhocracy_core.resources.itemversion import itemversion_meta
    appstructs = {IVersionable.__identifier__: {'follows': follows}}
    return ResourceFactory(itemversion_meta)(parent=parent,
                                                 appstructs=appstructs)


def make_forkable_itemversion(parent=None, follows=[]):
    from adhocracy_core.resources import ResourceFactory
    from adhocracy_core.sheets.versions import IForkableVersionable
    from adhocracy_core.resources.itemversion import itemversion_meta
    forkable_itemversion_metadata = itemversion_meta._replace(
        extended_sheets=(IForkableVersionable,)
    )
    appstructs = {IForkableVersionable.__identifier__: {'follows': follows}}
    return ResourceFactory(forkable_itemversion_metadata)(
        parent=parent, appstructs=appstructs)


@mark.usefixtures('integration')
class TestItem:

    @fixture
    def context(self, pool_with_catalogs):
        return pool_with_catalogs

    def make_one(self, context, registry, name='name'):
        from adhocracy_core.sheets.name import IName
        inst = registry.content.create(IItem.__identifier__,
                                       appstructs={},
                                       parent=context)
        return inst

    def test_create(self, context, registry):
        from adhocracy_core.sheets.tags import ITags

        item = self.make_one(context, registry)

        version0 = item['VERSION_0000000']
        assert IItemVersion.providedBy(version0)
        tags_sheet = registry.content.get_sheet(item, ITags)
        first = tags_sheet.get()['FIRST']
        last = tags_sheet.get()['LAST']
        assert first == version0
        assert last == version0

    def test_update_last_tag(self, context, registry):
        """Test that LAST tag is updated correctly."""
        from adhocracy_core.sheets.tags import ITags
        item = self.make_one(context, registry)
        version0 = item['VERSION_0000000']

        version1 = make_itemversion(parent=item, follows=[version0])

        tags_sheet = registry.content.get_sheet(item, ITags)
        last = tags_sheet.get()['LAST']
        assert last == version1
