import unittest

from pyramid import testing
from pytest import fixture
from pytest import mark


def test_create_mercator_catalog_indexes():
    from substanced.catalog import Keyword
    from . import MercatorCatalogIndexes
    inst = MercatorCatalogIndexes()
    assert isinstance(inst.mercator_requested_funding, Keyword)
    assert isinstance(inst.mercator_location, Keyword)


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_mercator.catalog')


@mark.usefixtures('integration')
def test_create_adhocracy_catalog(pool_graph, registry):
    from substanced.catalog import Catalog
    context = pool_graph
    catalogs = registry.content.create('Catalogs')
    context.add_service('catalogs', catalogs, registry=registry)
    catalogs.add_catalog('adhocracy')

    assert isinstance(catalogs['adhocracy'], Catalog)
    # default indexes
    assert 'tag' in catalogs['adhocracy']
    # mercator indexes
    assert 'mercator_requested_funding' in catalogs['adhocracy']
    assert 'mercator_budget' in catalogs['adhocracy']
    assert 'mercator_location' in catalogs['adhocracy']

