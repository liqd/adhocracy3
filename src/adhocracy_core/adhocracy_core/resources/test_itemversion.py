import unittest

from pyramid import testing

from adhocracy_core.interfaces import ISheetReferenceNewVersion
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.interfaces import IItemVersionNewVersionAdded
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.testing import create_event_listener


def test_itemversion_meta():
    from .itemversion import itemversion_metadata
    from .itemversion import IItemVersion
    from .itemversion import notify_new_itemversion_created
    import adhocracy_core.sheets
    meta = itemversion_metadata
    assert meta.iresource == IItemVersion
    assert meta.basic_sheets == [adhocracy_core.sheets.versions.IVersionable,
                                 adhocracy_core.sheets.metadata.IMetadata,
                                 ]
    assert notify_new_itemversion_created in meta.after_creation
    assert meta.use_autonaming


class ItemVersionIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy_core.testing import create_pool_with_graph
        config = testing.setUp()
        config.include('adhocracy_core.registry')
        config.include('adhocracy_core.events')
        config.include('adhocracy_core.changelog')
        config.include('adhocracy_core.catalog')
        config.include('adhocracy_core.sheets')
        config.include('adhocracy_core.resources.itemversion')
        config.include('adhocracy_core.resources.subscriber')
        self.config = config
        self.context = create_pool_with_graph()
        self.objectmap = self.context.__objectmap__
        self.graph = self.context.__graph__

    def tearDown(self):
        testing.tearDown()

    def _make_one(self, follows=[], appstructs={}, creator=None,
                  is_batchmode=False):
        from adhocracy_core.sheets.versions import IVersionable
        parent = self.context
        follow = {IVersionable.__identifier__: {'follows': follows}}
        appstructs = appstructs or {}
        appstructs.update(follow)
        itemversion = self.config.registry.content.create(
            IItemVersion.__identifier__,
            parent=parent,
            appstructs=appstructs,
            creator=creator,
            registry=self.config.registry,
            is_batchmode=is_batchmode,
        )
        return itemversion

    def test_registry_factory(self):
        content_types = self.config.registry.content.factory_types
        assert IItemVersion.__identifier__ in content_types

    def test_create(self):
        version_0 = self._make_one()
        assert IItemVersion.providedBy(version_0)

    def test_create_new_version(self):
        events = create_event_listener(self.config, IItemVersionNewVersionAdded)
        creator = self._make_one()

        version_0 = self._make_one()
        version_1 = self._make_one(follows=[version_0], creator=creator)

        assert len(events) == 1
        assert events[0].object == version_0
        assert events[0].new_version == version_1
        assert events[0].creator == creator

    def test_create_new_version_with_referencing_resources(self):
        events = create_event_listener(self.config,
                                       ISheetReferenceNewVersion)
        creator = self._make_one()

        version_0 = self._make_one()
        other_version_0 = self._make_one()
        self.objectmap.connect(other_version_0, version_0, SheetToSheet)
        self._make_one(follows=[version_0], creator=creator, is_batchmode=True)

        assert len(events) == 1
        assert events[0].creator == creator
        assert events[0].is_batchmode

    def test_autoupdate_with_referencing_items(self):
        # for more tests see adhocracy_core.resources.subscriber
        from adhocracy_core.sheets.document import ISection
        from adhocracy_core.resources.itemversion import itemversion_metadata
        from adhocracy_core.resources import add_resource_type_to_registry
        from adhocracy_core.sheets.versions import IVersionable
        from adhocracy_core.utils import get_sheet
        self.config.include('adhocracy_core.sheets.document')
        self.config.include('adhocracy_core.sheets.versions')
        metadata = itemversion_metadata._replace(extended_sheets=[ISection])
        add_resource_type_to_registry(metadata, self.config)
        referenced_v0 = self._make_one()
        referenceing_v0 = self._make_one(appstructs={ISection.__identifier__:
                                                     {'subsections': [referenced_v0]}})
        self.config.registry._transaction_changelog.clear()
        referenced_v1 = self._make_one(follows=[referenced_v0])

        referencing_v0_versions = get_sheet(referenceing_v0, IVersionable).get()
        assert len(referencing_v0_versions['followed_by']) == 1

