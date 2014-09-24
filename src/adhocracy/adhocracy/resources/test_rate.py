from pytest import mark
from pytest import fixture


def test_rateversion_meta():
    from .rate import rateversion_meta
    from adhocracy.sheets.rate import IRate
    assert rateversion_meta.extended_sheets == [IRate]


def test_rate_meta():
    from .rate import rate_meta
    from .rate import IRateVersion
    assert rate_meta.element_types == [IRateVersion]
    assert rate_meta.item_type == IRateVersion
    assert rate_meta.use_autonaming
    assert rate_meta.autonaming_prefix == 'rate_'


@fixture
def integration(config):
    config.include('adhocracy.registry')
    config.include('adhocracy.catalog')
    config.include('adhocracy.events')
    config.include('adhocracy.sheets')
    config.include('adhocracy.resources.rate')
    config.include('adhocracy.resources.tag')


@mark.usefixtures('integration')
def test_includeme_registry_register_factories(registry):
    from adhocracy.resources.rate import IRate
    from adhocracy.resources.rate import IRateVersion
    content_types = registry.content.factory_types
    assert IRate.__identifier__ in content_types
    assert IRateVersion.__identifier__ in content_types


@mark.usefixtures('integration')
def test_includeme_registry_create_rate(registry, pool_graph_catalog):
    from adhocracy.resources.rate import IRate
    pool = pool_graph_catalog
    assert registry.content.create(IRate.__identifier__, parent=pool)


@mark.usefixtures('integration')
def test_includeme_registry_create_rateversion(registry, pool_graph_catalog):
    from adhocracy.resources.rate import IRateVersion
    pool = pool_graph_catalog
    assert registry.content.create(IRateVersion.__identifier__, parent=pool)


@mark.usefixtures('integration')
def test_includeme_registry_search_rateversion(registry, pool_graph_catalog):
    from adhocracy.resources.rate import IRateVersion
    pool = pool_graph_catalog
    rate = registry.content.create(IRateVersion.__identifier__, parent=pool)
    rate_index = pool['catalogs']['adhocracy']['rate']
    rate_index.reindex_resource(rate)
    search_result = set(rate_index.eq(0).execute())
    assert rate in search_result
