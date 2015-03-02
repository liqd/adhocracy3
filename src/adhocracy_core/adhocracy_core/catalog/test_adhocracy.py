from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets.metadata')


def test_create_adhocracy_catalog_indexes():
    from substanced.catalog import Keyword
    from .adhocracy import AdhocracyCatalogIndexes
    from .adhocracy import Reference
    inst = AdhocracyCatalogIndexes()
    assert isinstance(inst.tag, Keyword)
    assert isinstance(inst.reference, Reference)


@mark.usefixtures('integration')
def test_create_adhocracy_catalog(pool_graph, registry):
    from substanced.catalog import Catalog
    context = pool_graph
    catalogs = registry.content.create('Catalogs')
    context.add_service('catalogs', catalogs, registry=registry)
    catalogs.add_catalog('adhocracy')

    assert isinstance(catalogs['adhocracy'], Catalog)
    assert 'tag' in catalogs['adhocracy']
    assert 'reference' in catalogs['adhocracy']
    assert 'rate' in catalogs['adhocracy']
    assert 'rates' in catalogs['adhocracy']
    assert 'creator' in catalogs['adhocracy']
    assert 'private_visibility' in catalogs['adhocracy']


class TestIndexCreator:

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    @fixture
    def mock_sheet(self, mock_sheet, registry):
        from adhocracy_core.sheets.metadata import IMetadata
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IMetadata)
        registry.content.get_sheet.return_value = mock_sheet
        return mock_sheet

    def test_creator_exists(self, context, mock_sheet):
        from .adhocracy import index_creator
        context['user1'] = testing.DummyResource()
        mock_sheet.get.return_value = {'creator': context['user1']}
        assert index_creator(context, 'default') == '/user1'

    def test_creator_does_not_exists(self, context, mock_sheet):
        from .adhocracy import index_creator
        context['user1'] = testing.DummyResource()
        mock_sheet.get.return_value = {'creator': ''}
        assert index_creator(context, 'default') == ''


@mark.usefixtures('integration')
def test_includeme_register_index_creator(registry):
    from adhocracy_core.sheets.metadata import IMetadata
    from substanced.interfaces import IIndexView
    assert registry.adapters.lookup((IMetadata,), IIndexView,
                                    name='adhocracy|creator')


def test_index_visibility_visible(context):
    from .adhocracy import index_visibility
    assert index_visibility(context, 'default') == ['visible']


def test_index_visibility_deleted(context):
    from .adhocracy import index_visibility
    assert index_visibility(context, 'default') == ['visible']
    context.deleted = True
    assert index_visibility(context, 'default') == ['deleted']


def test_index_visibility_hidden(context):
    from .adhocracy import index_visibility
    context.hidden = True
    assert index_visibility(context, 'default') == ['hidden']


def test_index_visibility_both(context):
    from .adhocracy import index_visibility
    context.deleted = True
    context.hidden = True
    assert sorted(index_visibility(context, 'default')) == ['deleted', 'hidden']


@mark.usefixtures('integration')
def test_includeme_register_index_visibilityreator(registry):
    from adhocracy_core.sheets.metadata import IMetadata
    from substanced.interfaces import IIndexView
    assert registry.adapters.lookup((IMetadata,), IIndexView,
                                    name='adhocracy|private_visibility')





