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


def create_new_reference_event(context,
                               registry,
                               isheet=IDummySheetAutoUpdate,
                               isheet_field='elements',
                               creator=None,
                               old_version=None,
                               new_version=None,
                               root_versions=None,
                               is_batchmode=False,
                               ):
    from zope.interface import verify
    from adhocracy_core.interfaces import ISheetReferenceNewVersion
    event = testing.DummyResource(__provides__= ISheetReferenceNewVersion,
                                  object=context,
                                  isheet=isheet,
                                  isheet_field=isheet_field,
                                  old_version=old_version,
                                  new_version=new_version,
                                  registry=registry,
                                  creator=creator,
                                  root_versions=root_versions or [],
                                  is_batchmode=is_batchmode,
                                  )
    assert verify.verifyObject(ISheetReferenceNewVersion, event)
    return event


@fixture
def version():
    """Return dummy resource with IItemVersion interfaces."""
    from adhocracy_core.interfaces import IItemVersion
    version = testing.DummyResource(__provides__=IItemVersion)
    return version


@fixture
def item(version):
    from adhocracy_core.interfaces import IItem
    item = testing.DummyResource(__provides__=IItem)
    item['version'] = version
    return item


@fixture
def event(changelog, context):
    registry = testing.DummyResource()
    registry._transaction_changelog = changelog
    event = testing.DummyResource(object=context, registry=registry)
    return event


class TestResourceCreatedAndAddedSubscriber:

    def _call_fut(self, event):
        from adhocracy_core.resources.subscriber import resource_created_and_added_subscriber
        return resource_created_and_added_subscriber(event)

    def test_call(self, event, changelog):
        self._call_fut(event)
        assert changelog['/'].created is True


class TestItemVersionCreated:

    def _call_fut(self, event):
        from adhocracy_core.resources.subscriber import itemversion_created_subscriber
        return itemversion_created_subscriber(event)

    def test_call_with_version_has_no_follows(self, event, changelog):
        event.new_version = None
        self._call_fut(event)
        assert changelog['/'].followed_by is None

    def test_call_with_version_has_follows(self, event, changelog):
        event.new_version = testing.DummyResource()
        self._call_fut(event)
        assert changelog['/'].followed_by is event.new_version


class TestResourceModifiedSubscriber:

    @fixture
    def context(self, context):
        from BTrees.Length import Length
        root = testing.DummyResource()
        root.__changed_descendants_counter__ = Length()
        root['parent'] = testing.DummyResource()
        root['parent'].__changed_descendants_counter__ = Length()
        root['parent']['child'] = context
        return context

    def _call_fut(self, event):
        from adhocracy_core.resources.subscriber import resource_modified_subscriber
        return resource_modified_subscriber(event)

    def test_set_modified_changelog(self, event, changelog):
        self._call_fut(event)
        assert changelog['/parent/child'].modified is True

    def test_dont_set_changed_descendants_for_context(self, event, changelog):
        self._call_fut(event)
        assert changelog['/parent/child'].changed_descendants is False

    def test_set_changed_descendants_changelog_for_parents(self, event,
                                                           changelog):
        self._call_fut(event)
        assert changelog['/parent'].changed_descendants is True
        assert changelog['/'].changed_descendants is True

    def test_set_changed_descendants_only_once(self, event, changelog):
        """Stop iterating all parents if `changed_descendants` is already set"""
        changelog['/parent'] = \
            changelog['parent']._replace(changed_descendants=True)
        self._call_fut(event)
        assert changelog['/parent'].changed_descendants is True
        assert changelog['/'].changed_descendants is False

    def test_increment_changed_descendants_counter_for_parents(self, event,
                                                               changelog):
        self._call_fut(event)
        assert changelog['/parent'].resource.\
                   __changed_descendants_counter__() == 1
        assert changelog['/'].resource.__changed_descendants_counter__() == 1


class TestResourceBackreferenceModifiedSubscriber:

    @fixture
    def context(self, context):
        from BTrees.Length import Length
        root = testing.DummyResource()
        root.__changed_descendants_counter__ = Length()
        root['parent'] = testing.DummyResource()
        root['parent'].__changed_descendants_counter__ = Length()
        root['parent']['child'] = context
        context.__changed_backrefs_counter__ = Length()
        return context

    def _call_fut(self, event):
        from .subscriber import resource_backreference_modified_subscriber
        return resource_backreference_modified_subscriber(event)

    def test_set_changed_backrefs_changelog(self, event, changelog):
        self._call_fut(event)
        assert changelog['/parent/child'].changed_backrefs is True

    def test_set_changed_backrefs_counter(self, event, changelog):
        self._call_fut(event)
        assert changelog['/parent/child'].resource.\
                   __changed_backrefs_counter__() == 1

    def test_set_changed_descendants_changelog_for_parents(self, event,
                                                           changelog):
        self._call_fut(event)
        assert changelog['/parent'].changed_descendants is True
        assert changelog['/'].changed_descendants is True

    def test_increment_changed_descendants_counter_for_parents(self, event,
                                                               changelog):
        self._call_fut(event)
        assert changelog['/parent'].resource.__changed_descendants_counter__() == 1
        assert changelog['/'].resource.__changed_descendants_counter__() == 1


def test_create_transaction_changelog():
    from adhocracy_core.interfaces import ChangelogMetadata
    from adhocracy_core.resources.subscriber import create_transaction_changelog
    changelog = create_transaction_changelog()
    changelog_metadata = changelog['/resource/path']
    assert isinstance(changelog_metadata, ChangelogMetadata)


def test_clear_transaction_changelog_exists(registry, changelog):
    from adhocracy_core.resources.subscriber import clear_transaction_changelog_after_commit_hook
    registry._transaction_changelog = changelog
    changelog['/'] = object()
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


class TestAutoupdateVersionableHasNewVersion:

    @fixture
    def registry(self, registry, mock_resource_registry, changelog):
        registry.content = mock_resource_registry
        registry._transaction_changelog = changelog
        return registry

    @fixture
    def mock_sheet(self, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IDummySheetAutoUpdate)
        mock_sheet.get.return_value = {'elements': []}
        return mock_sheet

    def _call_fut(self, event):
        from adhocracy_core.resources.subscriber import \
            autoupdate_versionable_has_new_version
        return autoupdate_versionable_has_new_version(event)

    def test_with_root_versions_not_in_subtree(self, version, mock_graph,
                                               registry):
        """Ingore event if object ist not in root_versions subtree."""
        root_version = testing.DummyResource()
        mock_graph.is_in_subtree.return_value = False
        version.__graph__ = mock_graph
        event = create_new_reference_event(version, registry,
                                           root_versions=[root_version])
        self._call_fut(event)
        mock_graph.is_in_subtree.assert_called_once_with(version, [root_version])
        assert registry.content.create.called is False

    def test_with_sheet_not_editable(self, version, registry, mock_sheet):
        """Ingore event if isheet ist not editable."""
        event = create_new_reference_event(version, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False)
        add_and_register_sheet(version, mock_sheet, registry)
        self._call_fut(event)
        assert registry.content.create.called is False

    def test_transaction_version_created_multiple_elements(
            self, version, registry, mock_sheet, changelog_meta):
        """Update version created in transaction (sheet field is list) """
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3,
                                           isheet_field='elements')
        add_and_register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        registry._transaction_changelog['/'] = \
            changelog_meta._replace(created=True)
        self._call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}
        assert registry.content.create.called is False

    def test_transation_version_created_single_element(
            self, version, registry, mock_sheet, changelog_meta):
        """Update version created in transaction (sheet field is single)"""
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3,
                                           isheet_field='element')
        add_and_register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'element': 2}
        registry._transaction_changelog['/'] = \
            changelog_meta._replace(created=True)
        self._call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'element': 3}
        assert registry.content.create.called is False

    def test_transaction_version_followed_by(
            self, version, registry, mock_sheet, changelog_meta):
        """Update followed_by version created in transaction."""
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        add_and_register_sheet(version, mock_sheet, registry)
        followedby = testing.DummyResource()
        add_and_register_sheet(followedby, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        registry._transaction_changelog['/'] =\
            changelog_meta._replace(followed_by=followedby)
        self._call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}
        assert registry.content.create.called is False

    def test_transaction_version_batchmode(
            self, item, version, registry, mock_sheet, changelog_meta):
        """Update items last_version created in transaction if batchmode.

           We could create forks if we update followedby/created during batch
           request. So we just take the last created item version.
        """
        from pyramid.traversal import resource_path
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3, is_batchmode=True)
        add_and_register_sheet(version, mock_sheet, registry)
        last_version = testing.DummyResource()
        add_and_register_sheet(last_version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        registry._transaction_changelog[resource_path(item)] =\
            changelog_meta._replace(last_version=last_version)
        self._call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}
        assert registry.content.create.called is False

    @fixture
    def mock_get_last_version(self, monkeypatch):
        import adhocracy_core.resources.subscriber
        mock = Mock(spec=adhocracy_core.utils.get_last_version)
        monkeypatch.setattr(adhocracy_core.resources.subscriber,
                            'get_last_version',
                            mock)
        return mock

    @fixture
    def mock_versionable_sheet(self, mock_sheet, sheet_meta):
        from copy import deepcopy
        from adhocracy_core.sheets.versions import IVersionable
        versionable = deepcopy(mock_sheet)
        versionable.get.return_value = {'follows': []}
        versionable.meta = sheet_meta._replace(isheet=IVersionable)
        return versionable

    def test_version_is_last_version(
            self, item, version, registry, mock_sheet, mock_versionable_sheet,
            mock_get_last_version):
        """If no version created in transaction and version is the items
           last_version create a new version.
        """
        from adhocracy_core.interfaces import IItemVersion
        from adhocracy_core.sheets.versions import IVersionable
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        add_and_register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        mock_get_last_version.return_value = version
        registry.content.get_sheets_all.return_value = [mock_sheet,
                                                        mock_versionable_sheet]
        self._call_fut(event)
        assert registry.content.create.call_args[0][0] == IItemVersion.__identifier__
        assert registry.content.create.call_args[1]['root_versions'] == event.root_versions
        assert registry.content.create.call_args[1]['registry'] == event.registry
        assert registry.content.create.call_args[1]['creator'] is event.creator
        assert registry.content.create.call_args[1]['parent'] is item
        assert registry.content.create.call_args[1]['is_batchmode'] == event.is_batchmode
        assert registry.content.create.call_args[1]['appstructs'] ==\
            {IDummySheetAutoUpdate.__identifier__: {'elements': [1, 3]},
             IVersionable.__identifier__: {'follows': [version]}}

    @fixture
    def mock_sheet_readonly(self, mock_sheet, sheet_meta):
        from copy import deepcopy
        mock_readonly = deepcopy(mock_sheet)
        isheet = IDummySheetNoAutoUpdate
        mock_readonly.meta = sheet_meta._replace(isheet=isheet,
                                                 creatable=False,
                                                 editable=False)
        return mock_readonly

    def test_version_is_last_version_with_readonly_sheet(
            self, version, registry, mock_sheet,
            mock_versionable_sheet, mock_get_last_version, mock_sheet_readonly):
        """If creating a new version, do not copy readonly sheets"""
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        add_and_register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        add_and_register_sheet(version, mock_sheet_readonly, registry)
        mock_get_last_version.return_value = version
        registry.content.get_sheets_all.return_value = [mock_sheet,
                                                        mock_versionable_sheet,
                                                        mock_sheet_readonly]
        self._call_fut(event)
        assert mock_sheet_readonly.meta.isheet.__identifier__ not in \
               registry.content.create.call_args[1]['appstructs']

    def test_version_is_not_last_version_but_has_same_references(
            self, version, registry, mock_sheet,
            mock_versionable_sheet, mock_get_last_version):
        """If no new version is created in transaction and version is not
           items last_version but has same references ignore
        """
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        add_and_register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        last = testing.DummyResource()
        add_and_register_sheet(last, mock_sheet, registry)
        mock_get_last_version.return_value = last
        registry.content.get_sheets_all.return_value = [mock_sheet,
                                                        mock_versionable_sheet]
        self._call_fut(event)
        assert registry.content.create.called is False

    def test_version_is_not_last_version_and_has_not_same_references(
            self, version, registry, mock_sheet,
            mock_versionable_sheet, mock_get_last_version):
        """If no new version is created in transaction and version is not
           items last_version but has same references raise
        """
        from adhocracy_core.exceptions import AutoUpdateNoForkAllowedError
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        add_and_register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        last = testing.DummyResource()
        add_and_register_sheet(last, mock_sheet, registry)
        mock_sheet.get.side_effect = [{'elements': [1, 2]}, {'elements': [11]},
                                      {'elements': [22]}]
        mock_get_last_version.return_value = last
        registry.content.get_sheets_all.return_value = [mock_sheet,
                                                        mock_versionable_sheet]
        with raises(AutoUpdateNoForkAllowedError) as err:
            self._call_fut(event)
        assert err.value.resource is version
        assert err.value.event is event


class TestAutoupdateNoneVersionableHasNewVersion:

    def registry(self, registry, mock_resource_registry):
        registry.content = mock_resource_registry
        return registry

    @fixture
    def mock_sheet(self, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IDummySheetAutoUpdate)
        mock_sheet.get.return_value = {'elements': []}
        return mock_sheet

    def _call_fut(self, event):
        from adhocracy_core.resources.subscriber import \
            autoupdate_non_versionable_has_new_version
        return autoupdate_non_versionable_has_new_version(event)

    def test_with_root_versions_not_in_subtree(self, version, mock_graph,
                                               registry, mock_sheet):
        """Ingore event if object ist not in root_versions subtree."""
        root_version = testing.DummyResource()
        mock_graph.is_in_subtree.return_value = False
        version.__graph__ = mock_graph
        event = create_new_reference_event(version, registry,
                                           root_versions=[root_version])
        add_and_register_sheet(version, mock_sheet, registry)
        self._call_fut(event)
        mock_graph.is_in_subtree.assert_called_once_with(version, [root_version])
        assert not mock_sheet.set.called

    def test_with_sheet_not_editable(self, version, registry, mock_sheet):
        """Ingore event if isheet ist not editable."""
        event = create_new_reference_event(version, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False)
        add_and_register_sheet(version, mock_sheet, registry)
        self._call_fut(event)
        assert not mock_sheet.set.called

    def test_multiple_elements(self, version, registry, mock_sheet):
        """Update version (sheet field is list) """
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3,
                                           isheet_field='elements')
        add_and_register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        self._call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}

    def test_single_element(self, version, registry, mock_sheet):
        """Update version (sheet field is list) """
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3,
                                           isheet_field='elements')
        add_and_register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        self._call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}


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
        assert mock_sheet.set.call_args[0][0] == {'groups': [default_group]}

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

    def test_newly_hidden(self, context, registry_with_changelog,
                          mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.interfaces import VisibilityChange
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': False, 'hidden': False}
        new_appstruct = {'deleted': False, 'hidden': True}
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry_with_changelog,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=None)
        metadata_modified_subscriber(event)
        assert mock_reindex.called
        assert (registry_with_changelog._transaction_changelog['/'].visibility
                is VisibilityChange.concealed)

    def test_newly_undeleted(self, context, registry_with_changelog,
                             mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.interfaces import VisibilityChange
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': True, 'hidden': False}
        new_appstruct = {'deleted': False, 'hidden': False}
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry_with_changelog,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=None)
        metadata_modified_subscriber(event)
        assert mock_reindex.called
        assert (registry_with_changelog._transaction_changelog['/'].visibility
                is VisibilityChange.revealed)

    def test_no_change_invisible(self, context, registry_with_changelog,
                                 mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.interfaces import VisibilityChange
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': False, 'hidden': True}
        new_appstruct = {'deleted': False, 'hidden': True}
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry_with_changelog,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=None)
        metadata_modified_subscriber(event)
        assert not mock_reindex.called
        assert (registry_with_changelog._transaction_changelog['/'].visibility
                is VisibilityChange.invisible)

    def test_no_change_visible(self, context, registry_with_changelog, request,
                               mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.interfaces import VisibilityChange
        from adhocracy_core.resources.subscriber import metadata_modified_subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': False, 'hidden': False}
        new_appstruct = {'deleted': False, 'hidden': False}
        request.has_permission = Mock(return_value=True)
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry_with_changelog,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=request)
        metadata_modified_subscriber(event)
        assert not mock_reindex.called
        assert (registry_with_changelog._transaction_changelog['/'].visibility
                is VisibilityChange.visible)


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
    assert subscriber.autoupdate_non_versionable_has_new_version.__name__ in handlers
    assert subscriber.autoupdate_versionable_has_new_version.__name__ in handlers
    assert subscriber.tag_created_and_added_or_modified_subscriber.__name__ in handlers
    assert subscriber.user_created_and_added_subscriber.__name__ in handlers
    assert subscriber.rate_backreference_modified_subscriber.__name__ in handlers
    assert subscriber.resource_backreference_modified_subscriber.__name__ in handlers
