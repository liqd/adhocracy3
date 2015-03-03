from pyramid import testing
from pytest import fixture
from pytest import mark


def _make_mercator_resource(context, location_appstruct={}, finance_appstruct={}):
    from adhocracy_core.interfaces import IResource
    from . import IMercatorSubResources
    from . import ILocation
    from . import IFinance
    from adhocracy_core.utils import get_sheet
    resource = testing.DummyResource(__provides__=[IResource,
                                                   IMercatorSubResources])
    context['res'] = resource
    sub_resources_sheet = get_sheet(resource, IMercatorSubResources)
    if location_appstruct:
        location_resource = testing.DummyResource(__provides__=[IResource,
                                                               ILocation])
        location_sheet = get_sheet(location_resource, ILocation)
        location_sheet.set(location_appstruct)
        context['location'] = location_resource
        sub_resources_sheet.set({'location': location_resource})
    if finance_appstruct:
        finance_resource = testing.DummyResource(__provides__=[IResource,
                                                               IFinance])
        finance_sheet = get_sheet(finance_resource, IFinance)
        finance_sheet.set(finance_appstruct)
        context['finance'] = finance_resource
        sub_resources_sheet.set({'finance': finance_resource})
    return resource


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
    config.include('adhocracy_mercator.sheets.mercator')


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


@mark.usefixtures('integration')
class TestMercatorLocationIndex:

    @fixture
    def context(self, pool_graph):
        return pool_graph

    def test_index_location_default(self, context):
        from . import index_location
        resource = _make_mercator_resource(context)
        result = index_location(resource, 'default')
        assert result == 'default'

    def test_index_location_is_linked_to_ruhr(self, context):
        from . import index_location
        resource = _make_mercator_resource(
            context,
            location_appstruct={'location_is_linked_to_ruhr': True})
        result = index_location(resource, 'default')
        assert result == ['linked_to_ruhr']

    def test_index_location_is_online_and_linked_to_ruhr(self, context):
        from . import index_location
        resource = _make_mercator_resource(
            context,
            location_appstruct={'location_is_online': True,
                               'location_is_linked_to_ruhr': True})
        result = index_location(resource, 'default')
        assert set(result) == set(['online', 'linked_to_ruhr'])

    def test_register_index_location(self, registry):
        from adhocracy_mercator.sheets.mercator import IMercatorSubResources
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((IMercatorSubResources,), IIndexView,
                                        name='adhocracy|mercator_location')


@mark.usefixtures('integration')
class TestMercatorRequestedFundingIndex:

    @fixture
    def context(self, pool_graph):
        return pool_graph

    def test_index_requested_funding_default(self, context):
        from . import index_requested_funding
        resource = _make_mercator_resource(context)
        result = index_requested_funding(resource, 'default')
        assert result == 'default'

    def test_index_requested_funding_lte_5000(self, context):
        from . import index_requested_funding
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'requested_funding': 5000})
        result = index_requested_funding(resource, 'default')
        assert result == ['5000']

    def test_index_requested_funding_lte_10000(self, context):
        from . import index_requested_funding
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'requested_funding': 10000})
        result = index_requested_funding(resource, 'default')
        assert result == ['10000']

    def test_index_requested_funding_lte_20000(self, context):
        from . import index_requested_funding
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'requested_funding': 20000})
        result = index_requested_funding(resource, 'default')
        assert result == ['20000']

    def test_index_requested_funding_lte_50000(self, context):
        from . import index_requested_funding
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'requested_funding': 50000})
        result = index_requested_funding(resource, 'default')
        assert result == ['50000']

    def test_index_requested_funding_gt_50000(self, context):
        from . import index_requested_funding
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'requested_funding': 50001})
        result = index_requested_funding(resource, 'default')
        assert result == 'default'

    def test_register_index_requested_funding(self, registry):
        from adhocracy_mercator.sheets.mercator import IMercatorSubResources
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((IMercatorSubResources,), IIndexView,
                                        name='adhocracy|mercator_requested_funding')



@mark.usefixtures('integration')
class TestMercatorBudgetIndex:

    @fixture
    def context(self, pool_graph):
        return pool_graph

    def test_index_budget_default(self, context):
        from . import index_budget
        resource = _make_mercator_resource(context)
        result = index_budget(resource, 'default')
        assert result == 'default'

    def test_index_budget_lte_5000(self, context):
        from . import index_budget
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'budget': 5000})
        result = index_budget(resource, 'default')
        assert result == ['5000']

    def test_index_budget_lte_10000(self, context):
        from . import index_budget
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'budget': 10000})
        result = index_budget(resource, 'default')
        assert result == ['10000']

    def test_index_budget_lte_20000(self, context):
        from . import index_budget
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'budget': 20000})
        result = index_budget(resource, 'default')
        assert result == ['20000']

    def test_index_budget_lte_50000(self, context):
        from . import index_budget
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'budget': 50000})
        result = index_budget(resource, 'default')
        assert result == ['50000']

    def test_index_budget_gt_50000(self, context):
        from . import index_budget
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'budget': 50001})
        result = index_budget(resource, 'default')
        assert result == ['above_50000']

    def test_register_index_budget(self, registry):
        from adhocracy_mercator.sheets.mercator import IMercatorSubResources
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((IMercatorSubResources,), IIndexView,
                                        name='adhocracy|mercator_budget')
