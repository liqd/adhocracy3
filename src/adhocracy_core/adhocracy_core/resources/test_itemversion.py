from pytest import fixture
from pytest import mark

from pyramid import testing

from adhocracy_core.interfaces import ISheetReferenceNewVersion
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.interfaces import IItemVersionNewVersionAdded
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.testing import create_event_listener


def test_itemversion_meta():
    from .itemversion import itemversion_meta
    from .itemversion import IItemVersion
    from .itemversion import notify_new_itemversion_created
    from .itemversion import update_last_tag
    import adhocracy_core.sheets
    meta = itemversion_meta
    assert meta.iresource == IItemVersion
    assert meta.basic_sheets == (adhocracy_core.sheets.metadata.IMetadata,
                                 adhocracy_core.sheets.versions.IVersionable,
                                 )
    assert meta.after_creation == (update_last_tag,
                                   notify_new_itemversion_created,
    )
    assert meta.use_autonaming


@fixture
def integration(integration):
    integration.include('adhocracy_core.changelog')
    return integration


@mark.usefixtures('integration')
class TestItemVersion:

    @fixture
    def item(self, pool_with_catalogs, registry):
        from adhocracy_core.resources.item import IItem
        item = registry.content.create(IItem.__identifier__,
                                       parent=pool_with_catalogs)
        return item

    @fixture
    def other_item(self, pool_with_catalogs, registry):
        from adhocracy_core.resources.item import IItem
        item = registry.content.create(IItem.__identifier__,
                                       parent=pool_with_catalogs)
        return item

    def make_one(self, registry, parent, follows=[], appstructs={}, creator=None,
                 is_batchmode=False):
        from adhocracy_core.sheets.versions import IVersionable
        follow = {IVersionable.__identifier__: {'follows': follows}}
        appstructs = appstructs or {}
        appstructs.update(follow)
        itemversion = registry.content.create(
            IItemVersion.__identifier__,
            parent=parent,
            appstructs=appstructs,
            creator=creator,
            registry=registry,
            is_batchmode=is_batchmode,
        )
        return itemversion

    def test_create(self, registry, item):
        version_0 = self.make_one(registry, item)
        assert IItemVersion.providedBy(version_0)

    def test_create_first_and_send_version_added_event(self, config,
                                                       registry, item):
        events = create_event_listener(config, IItemVersionNewVersionAdded)
        version_0 = self.make_one(registry, item)
        assert events[0].object == None
        assert events[0].new_version == version_0

    def test_create_following_and_send_version_added_event(self, config,
                                                           registry, item):
        version_0 = self.make_one(registry, item)
        events = create_event_listener(config, IItemVersionNewVersionAdded)
        version_1 = self.make_one(registry, item, follows=[version_0])
        assert events[0].object == version_0
        assert events[0].new_version == version_1

    def test_create_new_version_with_referencing_non_versionable(self, registry,
                                                                 config, item):
        from substanced.util import find_objectmap
        events = create_event_listener(config, ISheetReferenceNewVersion)
        creator = self.make_one(registry, item)

        version_0 = self.make_one(registry, item)
        other_version_0 = self.make_one(registry, item)
        om = find_objectmap(item)
        om.connect(other_version_0, version_0, SheetToSheet)
        self.make_one(registry, item,
                      follows=[version_0], creator=creator, is_batchmode=True)

        assert len(events) == 1
        assert events[0].creator == creator
        assert events[0].is_batchmode

    def test_autoupdate_with_referencing_versionable(self, config, registry,
                                                     item, other_item):
        # for more tests see adhocracy_core.resources.subscriber
        from pyramid.traversal import resource_path
        from adhocracy_core.sheets.document import IDocument
        from adhocracy_core.resources.itemversion import itemversion_meta
        from adhocracy_core.resources import add_resource_type_to_registry
        metadata = itemversion_meta._replace(extended_sheets=(IDocument,))
        add_resource_type_to_registry(metadata, config)
        referenced_v0 = self.make_one(registry, item)
        referenced_v0.v0 = 1
        appstructs = {IDocument.__identifier__: {'elements': [referenced_v0]}}
        referenceing_v0 = self.make_one(registry, other_item,
                                        appstructs=appstructs)
        referenceing_v0.vr0 = 1
        registry.changelog.clear()
        referenced_v1 = self.make_one(registry, item, follows=[referenced_v0])
        referenced_v1.v1 = 1

        referenceing_v0_path = resource_path(referenceing_v0)
        assert registry.changelog[referenceing_v0_path].followed_by

