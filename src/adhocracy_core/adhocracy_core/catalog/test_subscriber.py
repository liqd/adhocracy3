from unittest.mock import call
from unittest.mock import Mock
from pytest import fixture
from pytest import mark
from pyramid import testing


@fixture
def catalog():
    from substanced.interfaces import IService
    from substanced.interfaces import IFolder
    catalog = testing.DummyResource(__provides__=(IFolder, IService))
    catalog['adhocracy'] = testing.DummyResource(__provides__=(IFolder,
                                                               IService))
    catalog['adhocracy'].reindex_resource = Mock()
    return catalog


@fixture
def context(pool, catalog):
    pool['catalogs'] = catalog
    return pool


def test_reindex_tagged_with_removed_and_added_elements(context, catalog):
    from adhocracy_core.interfaces import ISheet
    from .subscriber import reindex_tagged
    registry = testing.DummyResource()
    added = testing.DummyResource()
    removed = testing.DummyResource()
    old = {'elements': [removed]}
    new = {'elements': [added]}
    event = testing.DummyResource(object=context,
                                  isheet=ISheet,
                                  registry=registry,
                                  old_appstruct=old,
                                  new_appstruct=new)
    reindex_tagged(event)
    assert catalog['adhocracy'].reindex_resource.call_count == 2


def test_reindex_rate_index(context, catalog):
    from .subscriber import reindex_rate
    event = testing.DummyResource(object=context)
    reindex_rate(event)
    assert catalog['adhocracy'].reindex_resource.call_count == 1


class TestReindexPrivateVisibility:

    @fixture
    def mock_reindex(self, monkeypatch):
        from . import subscriber
        mock_reindex = Mock(spec=subscriber._reindex_resource_and_descendants)
        monkeypatch.setattr(subscriber,
                            '_reindex_resource_and_descendants',
                            mock_reindex)
        return mock_reindex

    def call_fut(self, event):
        from .subscriber import reindex_private_visibility
        return reindex_private_visibility(event)

    def test_newly_hidden(self, context, registry_with_changelog,
                          mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.interfaces import VisibilityChange
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': False, 'hidden': False}
        new_appstruct = {'deleted': False, 'hidden': True}
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry_with_changelog,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=None)
        self.call_fut(event)
        assert mock_reindex.called
        assert (registry_with_changelog._transaction_changelog['/'].visibility
                is VisibilityChange.concealed)

    def test_newly_undeleted(self, context, registry_with_changelog,
                             mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.interfaces import VisibilityChange
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': True, 'hidden': False}
        new_appstruct = {'deleted': False, 'hidden': False}
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry_with_changelog,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=None)
        self.call_fut(event)
        assert mock_reindex.called
        assert (registry_with_changelog._transaction_changelog['/'].visibility
                is VisibilityChange.revealed)

    def test_no_change_invisible(self, context, registry_with_changelog,
                                 mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.interfaces import VisibilityChange
        from adhocracy_core.sheets.metadata import IMetadata
        old_appstruct = {'deleted': False, 'hidden': True}
        new_appstruct = {'deleted': False, 'hidden': True}
        event = ResourceSheetModified(object=context,
                                      isheet=IMetadata,
                                      registry=registry_with_changelog,
                                      old_appstruct=old_appstruct,
                                      new_appstruct=new_appstruct,
                                      request=None)
        self.call_fut(event)
        assert not mock_reindex.called
        assert (registry_with_changelog._transaction_changelog['/'].visibility
                is VisibilityChange.invisible)

    def test_no_change_visible(self, context, registry_with_changelog, request,
                               mock_reindex):
        from adhocracy_core.events import ResourceSheetModified
        from adhocracy_core.interfaces import VisibilityChange
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
        self.call_fut(event)
        assert not mock_reindex.called
        assert (registry_with_changelog._transaction_changelog['/'].visibility
                is VisibilityChange.visible)


class TestReindexResourceAndDescendants:

    @fixture
    def mock_path_query(self):
        mock_query = Mock()
        return mock_query

    @fixture
    def catalog(self, catalog, mock_path_query):
        from substanced.interfaces import IService
        from substanced.interfaces import IFolder
        from substanced.catalog.indexes import PathIndex
        catalog['system'] = testing.DummyResource(__provides__=(IFolder,
                                                                IService))
        mock_path_index = Mock(spec=PathIndex)
        mock_path_index.eq.return_value = mock_path_query
        catalog['system']['path'] = mock_path_index
        return catalog

    def call_fut(self, context):
        from .subscriber import _reindex_resource_and_descendants
        return _reindex_resource_and_descendants(context)

    def test_resource_and_descentdants_reindexed(self, context, catalog,
                                                 mock_path_query):
        from pyramid.traversal import resource_path
        child = testing.DummyResource()
        mock_path_query.execute.return_value = [context, child]
        self.call_fut(context)
        assert catalog['system']['path'].eq.call_args == \
               call(resource_path(context), include_origin=True)
        mock_reindex = catalog['adhocracy'].reindex_resource
        assert call(child) in mock_reindex.call_args_list
        assert mock_reindex.call_count == 2


@fixture()
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')


@mark.usefixtures('integration')
def test_register_subscriber(registry):
    from adhocracy_core.catalog import subscriber
    handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
    assert subscriber.reindex_tagged.__name__ in handlers
    assert subscriber.reindex_private_visibility.__name__ in handlers
    assert subscriber.reindex_rate.__name__ in handlers


