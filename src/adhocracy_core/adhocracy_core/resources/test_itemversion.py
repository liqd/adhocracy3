from pytest import fixture
from pytest import mark

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


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.changelog')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.itemversion')
    config.include('adhocracy_core.resources.subscriber')


@mark.usefixtures('integration')
class TestItemVersion:

    @fixture
    def context(self, pool_graph):
        return pool_graph

    def _make_one(self, config, parent, follows=[], appstructs={}, creator=None,
                  is_batchmode=False):
        from adhocracy_core.sheets.versions import IVersionable
        follow = {IVersionable.__identifier__: {'follows': follows}}
        appstructs = appstructs or {}
        appstructs.update(follow)
        itemversion = config.registry.content.create(
            IItemVersion.__identifier__,
            parent=parent,
            appstructs=appstructs,
            creator=creator,
            registry=config.registry,
            is_batchmode=is_batchmode,
        )
        return itemversion

    def test_registry_factory(self, config):
        content_types = config.registry.content.factory_types
        assert IItemVersion.__identifier__ in content_types

    def test_create(self, config, context):
        version_0 = self._make_one(config, context)
        assert IItemVersion.providedBy(version_0)

    def test_create_new_version(self, config, context):
        events = create_event_listener(config, IItemVersionNewVersionAdded)
        creator = self._make_one(config, context)

        version_0 = self._make_one(config, context)
        version_1 = self._make_one(config, context,
                                   follows=[version_0], creator=creator)

        assert len(events) == 1
        assert events[0].object == version_0
        assert events[0].new_version == version_1
        assert events[0].creator == creator

    def test_create_new_version_with_referencing_resources(self, config,
                                                           context):
        events = create_event_listener(config, ISheetReferenceNewVersion)
        creator = self._make_one(config, context)

        version_0 = self._make_one(config, context)
        other_version_0 = self._make_one(config, context)
        context.__objectmap__.connect(other_version_0, version_0, SheetToSheet)
        self._make_one(config, context,
                       follows=[version_0], creator=creator, is_batchmode=True)

        assert len(events) == 1
        assert events[0].creator == creator
        assert events[0].is_batchmode

    def test_autoupdate_with_referencing_items(self, config, context):
        # for more tests see adhocracy_core.resources.subscriber
        from adhocracy_core.sheets.document import ISection
        from adhocracy_core.resources.itemversion import itemversion_metadata
        from adhocracy_core.resources import add_resource_type_to_registry
        from adhocracy_core.sheets.versions import IVersionable
        from adhocracy_core.utils import get_sheet
        config.include('adhocracy_core.sheets.document')
        config.include('adhocracy_core.sheets.versions')
        metadata = itemversion_metadata._replace(extended_sheets=[ISection])
        add_resource_type_to_registry(metadata, config)
        referenced_v0 = self._make_one(config, context)
        appstructs={ISection.__identifier__: {'subsections': [referenced_v0]}}
        referenceing_v0 = self._make_one(config, context, appstructs=appstructs)
        config.registry.changelog.clear()
        referenced_v1 = self._make_one(config, context, follows=[referenced_v0])

        referencing_v0_versions = get_sheet(referenceing_v0, IVersionable).get()
        assert len(referencing_v0_versions['followed_by']) == 1

