from unittest.mock import call
from unittest.mock import Mock

from pytest import mark
from pytest import raises
from pytest import fixture

from pyramid import testing

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.testing import add_and_register_sheet


class IDummySheetAutoUpdate(ISheet, ISheetReferenceAutoUpdateMarker):
    pass


class IDummySheetNoAutoUpdate(ISheet):
    pass


def add_and_register_sheet(context, mock_sheet, registry):
    from zope.interface import alsoProvides
    from adhocracy_core.interfaces import IResourceSheet
    isheet = mock_sheet.meta.isheet
    alsoProvides(context, isheet)
    registry.registerAdapter(lambda x: mock_sheet, (isheet,),
                             IResourceSheet,
                             isheet.__identifier__)


def _create_new_version_event_with_isheet(context, isheet, registry, creator=None):
    from adhocracy_core.interfaces import ISheetReferencedItemHasNewVersion
    return testing.DummyResource(__provides__=
                                 ISheetReferencedItemHasNewVersion,
                                 object=context,
                                 isheet=isheet,
                                 isheet_field='elements',
                                 old_version=testing.DummyResource(),
                                 new_version=testing.DummyResource(),
                                 registry=registry,
                                 creator=creator,
                                 root_versions=[])

@fixture
def itemversion():
    """Return dummy resource with IItemVersion interfaces."""
    from adhocracy_core.interfaces import IItemVersion
    return testing.DummyResource(__provides__=IItemVersion)


@fixture
def event(transaction_changelog, context):
    registry = testing.DummyResource()
    registry._transaction_changelog = transaction_changelog
    event = testing.DummyResource(object=context, registry=registry)
    return event


class TestResourceCreatedAndAddedSubscriber:

    def _call_fut(self, event):
        from adhocracy_core.resources.subscriber import resource_created_and_added_subscriber
        return resource_created_and_added_subscriber(event)

    def test_call(self, event, transaction_changelog):
        self._call_fut(event)
        assert transaction_changelog['/'].created is True


class TestItemVersionCreated:

    def _call_fut(self, event):
        from adhocracy_core.resources.subscriber import itemversion_created_subscriber
        return itemversion_created_subscriber(event)

    def test_call_with_version_has_no_follows(self, event, transaction_changelog):
        event.new_version = None
        self._call_fut(event)
        assert transaction_changelog['/'].followed_by is None

    def test_call_with_version_has_follows(self, event, transaction_changelog):
        event.new_version = testing.DummyResource()
        self._call_fut(event)
        assert transaction_changelog['/'].followed_by is event.new_version


class TestResourceModifiedSubscriber:

    def _call_fut(self, event):
        from adhocracy_core.resources.subscriber import resource_modified_subscriber
        return resource_modified_subscriber(event)

    def test_call(self, event, transaction_changelog):
        self._call_fut(event)
        assert transaction_changelog['/'].modified is True


def test_create_transaction_changelog():
    from adhocracy_core.interfaces import ChangelogMetadata
    from adhocracy_core.resources.subscriber import create_transaction_changelog
    changelog = create_transaction_changelog()
    changelog_metadata = changelog['/resource/path']
    assert isinstance(changelog_metadata, ChangelogMetadata)


def test_clear_transaction_changelog_exists(registry, transaction_changelog):
    from adhocracy_core.resources.subscriber import clear_transaction_changelog_after_commit_hook
    registry._transaction_changelog = transaction_changelog
    transaction_changelog['/'] = object()
    clear_transaction_changelog_after_commit_hook(True, registry)
    assert len(registry._transaction_changelog) == 0


def test_clear_transaction_changelog_does_not_exists(registry):
    from adhocracy_core.resources.subscriber import clear_transaction_changelog_after_commit_hook
    assert clear_transaction_changelog_after_commit_hook(True, registry) is None


def test_default_changelog_metadata():
    from adhocracy_core.resources.subscriber import changelog_metadata
    assert changelog_metadata.modified is False
    assert changelog_metadata.created is False
    assert changelog_metadata.followed_by is None
    assert changelog_metadata.resource is None


class TestReferenceHasNewVersionSubscriberUnitTest:

    @fixture
    def registry(self, config, registry, mock_resource_registry, transaction_changelog):
        registry.content = mock_resource_registry
        registry._transaction_changelog = transaction_changelog
        return registry

    def _make_one(self, *args):
        from adhocracy_core.resources.subscriber import reference_has_new_version_subscriber
        return reference_has_new_version_subscriber(*args)

    def _create_new_version_event_for_autoupdate_sheet(self, context, registry, mock_sheet):
        from copy import deepcopy
        from adhocracy_core.sheets.versions import IVersionable
        event = _create_new_version_event_with_isheet(context, IDummySheetAutoUpdate, registry)
        sheet_autoupdate = deepcopy(mock_sheet)
        sheet_autoupdate.meta = mock_sheet.meta._replace(isheet=IDummySheetAutoUpdate)
        sheet_autoupdate.get.return_value = {'elements': [event.old_version],
                                             'element': event.old_version}
        add_and_register_sheet(context, sheet_autoupdate, registry)
        sheet_versionable = deepcopy(mock_sheet)
        sheet_versionable.meta = mock_sheet.meta._replace(isheet=IVersionable)
        sheet_versionable.get.return_value = {'follows': []}
        add_and_register_sheet(context, sheet_versionable, registry)
        registry.content.get_sheets_all.return_value = [sheet_autoupdate,
                                                        sheet_versionable]
        return event

    def test_call_versionable_with_autoupdate_sheet_once(self, itemversion, registry, mock_sheet):
        from adhocracy_core.sheets.versions import IVersionable
        event = self._create_new_version_event_for_autoupdate_sheet(itemversion, registry, mock_sheet)
        event.creator = object()

        self._make_one(event)

        factory = registry.content.create
        assert factory.call_count == 1
        parent = factory.call_args[1]['parent']
        assert parent is itemversion.__parent__
        appstructs = factory.call_args[1]['appstructs']
        assert appstructs[event.isheet.__identifier__]['elements'] == [event.new_version]
        assert appstructs[IVersionable.__identifier__] == {'follows': [itemversion]}
        creator = factory.call_args[1]['creator']
        assert creator == event.creator

    def test_call_versionable_with_autoupdate_sheet_with_single_reference(self, itemversion, registry, mock_sheet):
        event = self._create_new_version_event_for_autoupdate_sheet(itemversion, registry, mock_sheet)
        event.creator = object()
        event.isheet_field = 'element'

        self._make_one(event)

        factory = registry.content.create
        assert factory.call_count == 1

    def test_call_versionable_with_autoupdate_sheet_twice(self, itemversion, registry, mock_sheet, transaction_changelog):
        event = self._create_new_version_event_for_autoupdate_sheet(itemversion, registry, mock_sheet)
        self._make_one(event)

        event_second = self._create_new_version_event_for_autoupdate_sheet(itemversion, registry, mock_sheet)
        transaction_changelog['/'] = transaction_changelog['/']._replace(
            followed_by=event_second.new_version)
        registry._transaction_changelog = transaction_changelog
        self._make_one(event_second)

        factory = registry.content.create
        assert factory.call_count == 1

    def test_call_versionable_with_autoupdate_sheet_twice_without_transaction_changelog(self, itemversion, registry, mock_sheet):
        event = self._create_new_version_event_for_autoupdate_sheet(itemversion, registry, mock_sheet)
        self._make_one(event)

        event_second = self._create_new_version_event_for_autoupdate_sheet(itemversion, registry, mock_sheet)
        delattr(registry, '_transaction_changelog')
        self._make_one(event_second)

        factory = registry.content.create
        assert factory.call_count == 2

    def test_call_versionable_with_autoupdate_sheet_and_root_versions_and_not_is_insubtree(self,
            itemversion, mock_graph, registry, mock_sheet):
        mock_graph.is_in_subtree.return_value = False
        itemversion.__parent__=testing.DummyResource()
        itemversion.__graph__ = mock_graph
        event = self._create_new_version_event_for_autoupdate_sheet(itemversion, registry, mock_sheet)
        event.root_versions = [itemversion]

        self._make_one(event)

        assert not registry.content.create.called

    def test_call_versionable_with_autoupdate_sheet_but_readonly(self, itemversion, registry, mock_sheet):
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(itemversion, isheet, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False,
                                                   creatable=False,
                                                   isheet=isheet)
        add_and_register_sheet(itemversion, mock_sheet, registry)

        self._make_one(event)

        assert not registry.content.create.called

    def test_call_versionable_with_autoupdate_sheet_and_other_sheet_readonly(self, itemversion, registry, mock_sheet):
        event = self._create_new_version_event_for_autoupdate_sheet(itemversion, registry, mock_sheet)
        isheet_readonly = IDummySheetNoAutoUpdate
        mock_sheet.meta = mock_sheet.meta._replace(editable=False,
                                                   creatable=False,
                                                   isheet=isheet_readonly)
        add_and_register_sheet(itemversion, mock_sheet, registry)

        self._make_one(event)

        assert registry.content.create.called
        assert isheet_readonly.__identifier__ not in registry.content.create.call_args[1]['appstructs']

    def test_call_versionable_without_autoupdate_sheet(self, itemversion, registry, mock_sheet):
        isheet = IDummySheetNoAutoUpdate
        event = _create_new_version_event_with_isheet(itemversion, isheet, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False,
                                                   creatable=False,
                                                   isheet=isheet)
        add_and_register_sheet(itemversion, mock_sheet, registry)

        self._make_one(event)

        assert not registry.content.create.called

    def test_call_nonversionable_with_autoupdate_sheet(self, context, registry, mock_sheet):
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet, registry)
        mock_sheet.meta = mock_sheet.meta._replace(isheet=isheet)
        mock_sheet.get.return_value = {'elements': [event.old_version]}
        add_and_register_sheet(context, mock_sheet, registry)

        self._make_one(event)

        assert mock_sheet.set.call_args[0][0] == {'elements': [event.new_version]}

    def test_call_nonversionable_with_autoupdate_readonly(self, context, registry, mock_sheet):
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False,
                                                   creatable=False,
                                                   isheet=isheet)
        mock_sheet.get.return_value = {'elements': [event.old_version]}
        add_and_register_sheet(context, mock_sheet, registry)

        self._make_one(event)

        assert mock_sheet.set.called is False


class TestTagCreatedAndAddedOrModifiedSubscriber:

    @fixture
    def catalog(self):
        from substanced.interfaces import IService
        from substanced.interfaces import IFolder
        catalog = testing.DummyResource(
            __provides__=(IFolder, IService), __is_service__=True)
        catalog['adhocracy'] = testing.DummyResource(
            __provides__=(IFolder, IService), __is_service__=True)
        catalog['adhocracy'].reindex_resource = Mock()
        return catalog

    @fixture
    def context(self, pool, catalog):
        pool['catalogs'] = catalog
        return pool

    def call_fut(self, event):
        from adhocracy_core.resources.subscriber import\
            tag_created_and_added_or_modified_subscriber
        return tag_created_and_added_or_modified_subscriber(event)

    def test_with_removed_and_added_elements(self, context, catalog):
        registry = testing.DummyResource()
        added_tagged = testing.DummyResource()
        removed_tagged = testing.DummyResource()
        old = {'elements': [removed_tagged]}
        new = {'elements': [added_tagged]}
        event = testing.DummyResource(object=context,
                                      isheet=ISheet,
                                      registry=registry,
                                      old_appstruct=old,
                                      new_appstruct=new)
        self.call_fut(event)
        catalog['adhocracy'].reindex_resource.call_count == 2


class TestRateBackreferenceModifiedSubscriber:

    @fixture
    def catalog(self):
        from substanced.interfaces import IService
        from substanced.interfaces import IFolder
        catalog = testing.DummyResource(
            __provides__=(IFolder, IService), __is_service__=True)
        catalog['adhocracy'] = testing.DummyResource(
            __provides__=(IFolder, IService), __is_service__=True)
        catalog['adhocracy'].reindex_resource = Mock()
        return catalog

    @fixture
    def context(self, pool, catalog):
        pool['catalogs'] = catalog
        return pool

    def call_fut(self, event):
        from .subscriber import rate_backreference_modified_subscriber
        return rate_backreference_modified_subscriber(event)

    def test_index(self, context, catalog):
        event = testing.DummyResource(object=context)
        self.call_fut(event)
        catalog['adhocracy'].reindex_resource.call_count == 1


class TestAddDefaultGroupToUserSubscriber:

    @fixture
    def principals(self, pool, service):
        pool['principals'] = service
        pool['principals']['groups'] = service.clone()
        group = testing.DummyResource()
        pool['principals']['groups']['authenticated'] = group
        pool['principals']['users'] = service.clone()
        user = testing.DummyResource()
        pool['principals']['users']['000000'] = user
        return pool['principals']

    def call_fut(self, event):
        from adhocracy_core.resources.subscriber import\
            user_created_and_added_subscriber
        return user_created_and_added_subscriber(event)

    def test_default_group_exists(
            self, registry, principals, event, mock_sheet):
        from adhocracy_core.sheets.principal import IPermissions
        default_group = principals['groups']['authenticated']
        user = principals['users']['000000']
        event.object = user
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        add_and_register_sheet(event.object, mock_sheet, registry)
        mock_sheet.get.return_value = {'groups': []}
        self.call_fut(event)
        assert mock_sheet.set.call_args[0] == ({'groups': [default_group]},)


    def test_default_group_not_exists(
            self, registry, principals, event, mock_sheet):
        from adhocracy_core.sheets.principal import IPermissions
        del principals['groups']['authenticated']
        user = principals['users']['000000']
        event.object = user
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        add_and_register_sheet(event.object, mock_sheet, registry)
        mock_sheet.get.return_value = {'groups': []}
        self.call_fut(event)
        assert mock_sheet.set.called is False


class TestMetadataModifiedSubscriber:

    @fixture
    def mock_reindex(self, monkeypatch):
        from adhocracy_core.resources import subscriber
        mock_reindex = Mock(spec=subscriber._reindex_resource_and_descendants)
        monkeypatch.setattr(subscriber,
                            '_reindex_resource_and_descendants',
                            mock_reindex)
        return mock_reindex

    def test_newly_hidden(self, context, registry, request, mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': False, 'hidden': False}
        new_appstruct = {'deleted': False, 'hidden': True}
        request.has_permission = Mock(return_value=True)
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=request)
        metadata_modified_subscriber(event)
        assert context.deleted is False
        assert context.hidden is True
        assert mock_reindex.called

    def test_newly_undeleted(self, context, registry, request, mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': True, 'hidden': False}
        new_appstruct = {'deleted': False, 'hidden': False}
        request.has_permission = Mock(return_value=True)
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=request)
        metadata_modified_subscriber(event)
        assert context.deleted is False
        assert context.hidden is False
        assert mock_reindex.called

    def test_no_change(self, context, registry, request, mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': False, 'hidden': True}
        new_appstruct = {'deleted': False, 'hidden': True}
        request.has_permission = Mock(return_value=True)
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=request)
        metadata_modified_subscriber(event)
        assert context.deleted is False
        assert context.hidden is True
        assert not mock_reindex.called

    def test_hiding_requires_permission(self, context, registry, request,
                                        mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        import colander
        old_appstruct = {'deleted': False, 'hidden': False}
        new_appstruct = {'deleted': False, 'hidden': True}
        request.has_permission = Mock(return_value=False)
        context.deleted = None
        context.hidden = None
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=request)
        with raises(colander.Invalid):
            metadata_modified_subscriber(event)
        assert context.deleted is None
        assert context.hidden is None
        assert not mock_reindex.called

    def test_deletion_doesnt_require_permission(self, context, registry,
                                               request, mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': False, 'hidden': False}
        new_appstruct = {'deleted': True, 'hidden': False}
        request.has_permission = Mock(return_value=False)
        context.deleted = None
        context.hidden = None
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=request)
        metadata_modified_subscriber(event)
        assert context.deleted is True
        assert context.hidden is False
        assert mock_reindex.called

    def test_no_hiding_without_request(self, context, registry, mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': False, 'hidden': False}
        new_appstruct = {'deleted': False, 'hidden': True}
        context.deleted = None
        context.hidden = None
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=None)
        metadata_modified_subscriber(event)
        assert context.deleted is None
        assert context.hidden is None
        assert not mock_reindex.called


class TestReindexResourceAndDescendants:

    @fixture
    def mock_reindex_resource(self, monkeypatch, pool_graph_catalog):
        from substanced.util import find_catalog
        adhocracy_catalog = find_catalog(pool_graph_catalog, 'adhocracy')
        mock_reindex_resource = Mock(spec=adhocracy_catalog.reindex_resource)
        monkeypatch.setattr(adhocracy_catalog,
                            'reindex_resource',
                            mock_reindex_resource)
        return mock_reindex_resource

    def test_resource_reindexed(self, config, context, pool_graph_catalog,
                                mock_reindex_resource):
        from adhocracy_core.resources.subscriber import _reindex_resource_and_descendants
        config.include('adhocracy_core.catalog')
        pool_graph_catalog['res'] = context
        _reindex_resource_and_descendants(context)
        mock_reindex_resource.assert_called_with(context)
        assert mock_reindex_resource.call_count == 1

    def test_child_reindexed(self, config, pool, pool_graph_catalog,
                                mock_reindex_resource):
        from adhocracy_core.interfaces import IResource
        from adhocracy_core.resources.subscriber import _reindex_resource_and_descendants
        config.include('adhocracy_core.catalog')
        child = testing.DummyResource(__provides__=IResource)
        pool['child'] = child
        pool_graph_catalog['res'] = pool
        _reindex_resource_and_descendants(pool)
        assert mock_reindex_resource.call_count == 2
        assert call(child) in mock_reindex_resource.call_args_list

    def test_grandchild_reindexed(self, config, pool, pool_graph_catalog,
                                  mock_reindex_resource):
        from substanced.interfaces import IFolder
        from adhocracy_core.interfaces import IPool
        from adhocracy_core.interfaces import IResource
        from adhocracy_core.resources.subscriber import _reindex_resource_and_descendants
        from adhocracy_core.testing import DummyPool
        config.include('adhocracy_core.catalog')
        grandchild = testing.DummyResource(__provides__=IResource)
        childpool = DummyPool(__provides__=(IPool, IFolder))
        childpool['grandchild'] = grandchild
        pool['childpool'] = childpool
        pool_graph_catalog['res'] = pool
        _reindex_resource_and_descendants(pool)
        assert mock_reindex_resource.call_count == 3
        assert call(grandchild) in mock_reindex_resource.call_args_list


@fixture()
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.resources.subscriber')


@mark.usefixtures('integration')
def test_add_transaction_changelog(registry):
    assert hasattr(registry, '_transaction_changelog')


@mark.usefixtures('integration')
def test_register_subscriber(registry):
    from adhocracy_core.resources import subscriber
    handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
    assert subscriber.resource_created_and_added_subscriber.__name__ in handlers
    assert subscriber.itemversion_created_subscriber.__name__ in handlers
    assert subscriber.resource_modified_subscriber.__name__ in handlers
    assert subscriber.reference_has_new_version_subscriber.__name__ in handlers
    assert subscriber.tag_created_and_added_or_modified_subscriber.__name__ in handlers
    assert subscriber.user_created_and_added_subscriber.__name__ in handlers
    assert subscriber.rate_backreference_modified_subscriber.__name__ in handlers
