from pyramid import testing
from pytest import fixture
from pytest import mark


def _make_mercator_resource(context,
                            location_appstruct={},
                            finance_appstruct={}):
    from adhocracy_core.interfaces import IResource
    from adhocracy_mercator.sheets.mercator import IMercatorSubResources
    from adhocracy_mercator.sheets.mercator import ILocation
    from adhocracy_mercator.sheets.mercator import IFinance
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
    from .adhocracy import MercatorCatalogIndexes
    inst = MercatorCatalogIndexes()
    assert isinstance(inst.mercator_requested_funding, Keyword)
    assert isinstance(inst.mercator_location, Keyword)
    assert isinstance(inst.mercator_topic, Keyword)


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
    def context(self, pool_with_catalogs):
        return pool_with_catalogs

    def test_index_location_default(self, context):
        from .adhocracy import index_location
        resource = _make_mercator_resource(context)
        result = index_location(resource, 'default')
        assert result == 'default'

    def test_index_location_is_linked_to_ruhr(self, context):
        from .adhocracy import index_location
        resource = _make_mercator_resource(
            context,
            location_appstruct={'location_is_linked_to_ruhr': True})
        result = index_location(resource, 'default')
        assert result == ['linked_to_ruhr']

    def test_index_location_is_online_and_linked_to_ruhr(self, context):
        from .adhocracy import index_location
        resource = _make_mercator_resource(
            context,
            location_appstruct={'location_is_online': True,
                                'location_is_linked_to_ruhr': True})
        result = index_location(resource, 'default')
        assert set(result) == {'online', 'linked_to_ruhr'}

    def test_register_index_location(self, registry):
        from adhocracy_mercator.sheets.mercator import IMercatorSubResources
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((IMercatorSubResources,), IIndexView,
                                        name='adhocracy|mercator_location')


@mark.usefixtures('integration')
class TestMercatorRequestedFundingIndex:

    @fixture
    def context(self, pool_with_catalogs):
        return pool_with_catalogs

    def test_index_requested_funding_default(self, context):
        from .adhocracy import index_requested_funding
        resource = _make_mercator_resource(context)
        result = index_requested_funding(resource, 'default')
        assert result == 'default'

    def test_index_requested_funding_lte_5000(self, context):
        from .adhocracy import index_requested_funding
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'requested_funding': 5000})
        result = index_requested_funding(resource, 'default')
        assert result == [5000]

    def test_index_requested_funding_lte_10000(self, context):
        from .adhocracy import index_requested_funding
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'requested_funding': 10000})
        result = index_requested_funding(resource, 'default')
        assert result == [10000]

    def test_index_requested_funding_lte_20000(self, context):
        from .adhocracy import index_requested_funding
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'requested_funding': 20000})
        result = index_requested_funding(resource, 'default')
        assert result == [20000]

    def test_index_requested_funding_lte_50000(self, context):
        from .adhocracy import index_requested_funding
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'requested_funding': 50000})
        result = index_requested_funding(resource, 'default')
        assert result == [50000]

    def test_index_requested_funding_gt_50000(self, context):
        from .adhocracy import index_requested_funding
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
    def context(self, pool_with_catalogs):
        return pool_with_catalogs

    def test_index_budget_default(self, context):
        from .adhocracy import index_budget
        resource = _make_mercator_resource(context)
        result = index_budget(resource, 'default')
        assert result == 'default'

    def test_index_budget_lte_5000(self, context):
        from .adhocracy import index_budget
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'budget': 5000})
        result = index_budget(resource, 'default')
        assert result == ['5000']

    def test_index_budget_lte_10000(self, context):
        from .adhocracy import index_budget
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'budget': 10000})
        result = index_budget(resource, 'default')
        assert result == ['10000']

    def test_index_budget_lte_20000(self, context):
        from .adhocracy import index_budget
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'budget': 20000})
        result = index_budget(resource, 'default')
        assert result == ['20000']

    def test_index_budget_lte_50000(self, context):
        from .adhocracy import index_budget
        resource = _make_mercator_resource(
            context,
            finance_appstruct={'budget': 50000})
        result = index_budget(resource, 'default')
        assert result == ['50000']

    def test_index_budget_gt_50000(self, context):
        from .adhocracy import index_budget
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


def _make_mercator2_resource(context,
                             location_appstruct={},
                             financial_planning_appstruct={}):
    from adhocracy_core.interfaces import IResource
    from adhocracy_mercator.sheets.mercator2 import ILocation
    from adhocracy_mercator.sheets.mercator2 import IFinancialPlanning
    from adhocracy_core.utils import get_sheet
    resource = testing.DummyResource(__provides__=[IResource,
                                                   ILocation,
                                                   IFinancialPlanning])
    context['res'] = resource
    location_sheet = get_sheet(resource, ILocation)
    location_sheet.set(location_appstruct)
    financial_planning_sheet = get_sheet(resource, IFinancialPlanning)
    financial_planning_sheet.set(financial_planning_appstruct)
    return resource


@mark.usefixtures('integration')
class TestMercator2LocationIndex:

    @fixture
    def context(self, pool_with_catalogs):
        return pool_with_catalogs

    def test_index_location_default(self, context):
        from .adhocracy import mercator2_index_location
        resource = _make_mercator2_resource(context)
        result = mercator2_index_location(resource, 'default')
        assert result == 'default'

    def test_index_location_is_linked_to_ruhr(self, context):
        from .adhocracy import mercator2_index_location
        resource = _make_mercator2_resource(
            context,
            location_appstruct={'has_link_to_ruhr': True})
        result = mercator2_index_location(resource, 'default')
        assert result == ['linked_to_ruhr']

    def test_index_location_is_online_and_linked_to_ruhr(self, context):
        from .adhocracy import mercator2_index_location
        resource = _make_mercator2_resource(
            context,
            location_appstruct={'is_online': True,
                                'has_link_to_ruhr': True})
        result = mercator2_index_location(resource, 'default')
        assert set(result) == {'online', 'linked_to_ruhr'}

    def test_index_location_is_specific(self, context):
        from .adhocracy import mercator2_index_location
        resource = _make_mercator2_resource(
            context,
            location_appstruct={'location': 'Berlin',
                                'is_online': False,
                                'has_link_to_ruhr': False})
        result = mercator2_index_location(resource, 'default')
        assert set(result) == {'specific'}

    def test_register_index_location(self, registry):
        from adhocracy_mercator.sheets.mercator2 import ILocation
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((ILocation,), IIndexView,
                                        name='adhocracy|mercator_location')


@mark.usefixtures('integration')
class TestMercator2RequestedFundingIndex:

    @fixture
    def context(self, pool_with_catalogs):
        return pool_with_catalogs

    def test_index_requested_funding_default(self, context):
        from .adhocracy import mercator2_index_requested_funding
        resource = _make_mercator2_resource(context)
        result = mercator2_index_requested_funding(resource, 'default')
        assert result == [5000]

    def test_index_requested_funding_lte_5000(self, context):
        from .adhocracy import mercator2_index_requested_funding
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'requested_funding': 5000})
        result = mercator2_index_requested_funding(resource, 'default')
        assert result == [5000]

    def test_index_requested_funding_lte_10000(self, context):
        from .adhocracy import mercator2_index_requested_funding
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'requested_funding': 10000})
        result = mercator2_index_requested_funding(resource, 'default')
        assert result == [10000]

    def test_index_requested_funding_lte_20000(self, context):
        from .adhocracy import mercator2_index_requested_funding
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'requested_funding': 20000})
        result = mercator2_index_requested_funding(resource, 'default')
        assert result == [20000]

    def test_index_requested_funding_lte_50000(self, context):
        from .adhocracy import mercator2_index_requested_funding
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'requested_funding': 50000})
        result = mercator2_index_requested_funding(resource, 'default')
        assert result == [50000]

    def test_index_requested_funding_gt_50000(self, context):
        from .adhocracy import mercator2_index_requested_funding
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'requested_funding': 50001})
        result = mercator2_index_requested_funding(resource, 'default')
        assert result == 'default'

    def test_register_mercator2_index_requested_funding(self, registry):
        from adhocracy_mercator.sheets.mercator2 import IFinancialPlanning
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((IFinancialPlanning,), IIndexView,
                                        name='adhocracy|mercator_requested_funding')


@mark.usefixtures('integration')
class TestMercator2BudgetIndex:

    @fixture
    def context(self, pool_with_catalogs):
        return pool_with_catalogs

    def test_index_budget_default(self, context):
        from .adhocracy import mercator2_index_budget
        resource = _make_mercator2_resource(context)
        result = mercator2_index_budget(resource, 'default')
        assert result == ['5000']

    def test_index_budget_lte_5000(self, context):
        from .adhocracy import mercator2_index_budget
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'budget': 5000})
        result = mercator2_index_budget(resource, 'default')
        assert result == ['5000']

    def test_index_budget_lte_10000(self, context):
        from .adhocracy import mercator2_index_budget
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'budget': 10000})
        result = mercator2_index_budget(resource, 'default')
        assert result == ['10000']

    def test_index_budget_lte_20000(self, context):
        from .adhocracy import mercator2_index_budget
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'budget': 20000})
        result = mercator2_index_budget(resource, 'default')
        assert result == ['20000']

    def test_index_budget_lte_50000(self, context):
        from .adhocracy import mercator2_index_budget
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'budget': 50000})
        result = mercator2_index_budget(resource, 'default')
        assert result == ['50000']

    def test_index_budget_gt_50000(self, context):
        from .adhocracy import mercator2_index_budget
        resource = _make_mercator2_resource(
            context,
            financial_planning_appstruct={'budget': 50001})
        result = mercator2_index_budget(resource, 'default')
        assert result == ['above_50000']

    def test_register_index_budget(self, registry):
        from adhocracy_mercator.sheets.mercator2 import IFinancialPlanning
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((IFinancialPlanning,), IIndexView,
                                        name='adhocracy|mercator_budget')


class TestMercator2IndexTopic:

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    @fixture
    def mock_topic_sheet(self, registry, mock_sheet):
        registry.content.get_sheet.return_value = mock_sheet
        return mock_sheet

    def call_fut(self, *args):
        from .adhocracy import mercator2_index_topic
        return mercator2_index_topic(*args)

    def test_return_default_if_topic_none(self, context, mock_topic_sheet):
        mock_topic_sheet.get.return_value = {'topic': None}
        assert self.call_fut(context, 'default') == 'default'

    def test_return_topic(self, context, mock_topic_sheet):
        mock_topic_sheet.get.return_value = {'topic': 'other'}
        assert self.call_fut(context, 'default') == ['other']

    @mark.usefixtures('integration')
    def test_register(self, registry):
        from adhocracy_mercator.sheets.mercator2 import ITopic
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((ITopic,), IIndexView,
                                        name='adhocracy|mercator_topic')