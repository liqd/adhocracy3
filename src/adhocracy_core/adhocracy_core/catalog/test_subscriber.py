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


@fixture
def event(context):
    return testing.DummyResource(object=context)


def test_reindex_tagged_with_removed_and_added_elements(event, catalog):
    from .subscriber import reindex_tag
    reindex_tag(event)
    assert catalog['adhocracy'].reindex_resource.call_count == 1


def test_reindex_rate_index(event, catalog):
    from .subscriber import reindex_rate
    reindex_rate(event)
    assert catalog['adhocracy'].reindex_resource.call_count == 1


@fixture
def mock_reindex(monkeypatch):
    from . import subscriber
    mock_reindex = Mock(spec=subscriber._reindex_resource_and_descendants)
    monkeypatch.setattr(subscriber,
                        '_reindex_resource_and_descendants',
                        mock_reindex)
    return mock_reindex


@fixture
def mock_visibility(monkeypatch):
    from . import subscriber
    mock_visibility = Mock(spec=subscriber.get_visibility_change)
    monkeypatch.setattr(subscriber,
                        'get_visibility_change',
                        mock_visibility)
    return mock_visibility


def test_reindex_visibility_concealed(event, mock_reindex, mock_visibility):
    from adhocracy_core.interfaces import VisibilityChange
    from .subscriber import reindex_visibility
    mock_visibility.return_value = VisibilityChange.concealed
    reindex_visibility(event)
    assert mock_reindex.called


def test_reindex_visibility_revealed(event, mock_reindex, mock_visibility):
    from adhocracy_core.interfaces import VisibilityChange
    from .subscriber import reindex_visibility
    mock_visibility.return_value = VisibilityChange.revealed
    reindex_visibility(event)
    assert mock_reindex.called


def test_reindex_visibility_invisible(event, mock_reindex, mock_visibility):
    from adhocracy_core.interfaces import VisibilityChange
    from .subscriber import reindex_visibility
    mock_visibility.return_value = VisibilityChange.invisible
    reindex_visibility(event)
    assert not mock_reindex.called


def test_reindex_visibility_visible(event, mock_reindex, mock_visibility):
    from adhocracy_core.interfaces import VisibilityChange
    from .subscriber import reindex_visibility
    mock_visibility.return_value = VisibilityChange.visible
    reindex_visibility(event)
    assert not mock_reindex.called


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
    assert subscriber.reindex_tag.__name__ in handlers
    assert subscriber.reindex_visibility.__name__ in handlers
    assert subscriber.reindex_rate.__name__ in handlers


