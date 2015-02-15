from pytest import fixture
from pytest import mark


def test_create_adhocracy_catalog_indexes():
    from substanced.catalog import Keyword
    from .adhocracy import AdhocracyCatalogIndexes
    from .adhocracy import Reference
    inst = AdhocracyCatalogIndexes()
    assert isinstance(inst.tag, Keyword)
    assert isinstance(inst.reference, Reference)


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.catalog')


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

