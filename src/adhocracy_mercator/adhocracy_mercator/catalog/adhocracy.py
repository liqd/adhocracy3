"""Adhocracy catalog extensions."""
from pyramid.threadlocal import get_current_registry
from substanced.catalog import Keyword

from adhocracy_core.catalog.adhocracy import AdhocracyCatalogIndexes
from adhocracy_core.rest.schemas import INDEX_EXAMPLE_VALUES
from adhocracy_core.interfaces import IResource
from adhocracy_mercator.sheets.mercator import IMercatorSubResources
from adhocracy_mercator.sheets.mercator import IFinance
from adhocracy_mercator.sheets.mercator import ILocation
from adhocracy_mercator import sheets


INDEX_EXAMPLE_VALUES['mercator_requested_funding'] = 1


class MercatorCatalogIndexes(AdhocracyCatalogIndexes):
    """Mercator indexes for the adhocracy catalog."""

    mercator_location = Keyword()
    mercator_requested_funding = Keyword()
    mercator_budget = Keyword()
    mercator_topic = Keyword()


LOCATION_INDEX_KEYWORDS = ['specific', 'online', 'linked_to_ruhr']


def index_location(resource, default) -> list:
    """Return search index keywords based on the "location_is_..." fields."""
    registry = get_current_registry(resource)
    location = registry.content.get_sheet_field(resource,
                                                IMercatorSubResources,
                                                'location')
    # TODO: Why is location '' in the first pass of that function
    # during MercatorProposal create?
    if location is None or location == '':
        return default
    locations = []
    for keyword in LOCATION_INDEX_KEYWORDS:
        is_used = registry.content.get_sheet_field(location,
                                                   ILocation,
                                                   'location_is_' + keyword)
        if is_used:
            locations.append(keyword)
    return locations if locations else default

BUDGET_INDEX_LIMIT_KEYWORDS = [5000, 10000, 20000, 50000]


def index_requested_funding(resource: IResource, default) -> int:
    """Return search index keyword based on the "requested_funding" field."""
    # TODO: Why is finance '' in the first pass of that function
    # during MercatorProposal create?
    # This sounds like a bug, the default value for References is None,
    registry = get_current_registry(resource)
    finance = registry.content.get_sheet_field(resource,
                                               IMercatorSubResources,
                                               'finance')
    if finance is None or finance == '':
        return default
    funding = registry.content.get_sheet_field(finance,
                                               IFinance,
                                               'requested_funding')
    for limit in BUDGET_INDEX_LIMIT_KEYWORDS:
        if funding <= limit:
            return [limit]
    return default


def index_budget(resource: IResource, default) -> str:
    """Return search index keyword based on the "budget" field.

    The returned values are the same values as per the "requested_funding"
    field, or "above_50000" if the total budget value is more than 50,000 euro.
    """
    registry = get_current_registry(resource)
    finance = registry.content.get_sheet_field(resource,
                                               IMercatorSubResources,
                                               'finance')
    if finance is None or finance == '':
        return default
    funding = registry.content.get_sheet_field(finance,
                                               IFinance,
                                               'budget')
    for limit in BUDGET_INDEX_LIMIT_KEYWORDS:
        if funding <= limit:
            return [str(limit)]
    return ['above_50000']


def mercator2_index_location(resource, default) -> list:
    """Return search index keywords based on the location's fields."""
    registry = get_current_registry(resource)
    locations = []
    if registry.content.get_sheet_field(resource,
                                        sheets.mercator2.ILocation,
                                        'is_online'):
        locations.append('online')
    if registry.content.get_sheet_field(resource,
                                        sheets.mercator2.ILocation,
                                        'has_link_to_ruhr'):
        locations.append('linked_to_ruhr')
    if registry.content.get_sheet_field(resource,
                                        sheets.mercator2.ILocation,
                                        'location') is not '':
        locations.append('specific')
    return locations if locations else default


def mercator2_index_requested_funding(resource: IResource, default) -> int:
    """Return search index keyword based on the "requested_funding" field."""
    registry = get_current_registry(resource)
    requested_funding = registry.content.get_sheet_field(
        resource,
        sheets.mercator2.IFinancialPlanning,
        'requested_funding')
    for limit in BUDGET_INDEX_LIMIT_KEYWORDS:
        if requested_funding <= limit:
            return [limit]
    return default


def mercator2_index_budget(resource: IResource, default) -> str:
    """Return search index keyword based on the "budget" field.

    The returned values are the same values as per the "requested_funding"
    field, or "above_50000" if the total budget value is more than 50,000 euro.
    """
    registry = get_current_registry(resource)
    budget = registry.content.get_sheet_field(
        resource,
        sheets.mercator2.IFinancialPlanning,
        'budget')
    for limit in BUDGET_INDEX_LIMIT_KEYWORDS:
        if budget <= limit:
            return [str(limit)]
    return ['above_50000']


def mercator2_index_topic(resource: IResource, default) -> [str]:
    """Return search index keywords based on the "topic" field."""
    registry = get_current_registry(resource)
    topic = registry.content.get_sheet_field(resource,
                                             sheets.mercator2.ITopic,
                                             'topic')
    if topic == []:
        return default
    return topic


def includeme(config):
    """Register catalog utilities and index functions."""
    config.add_catalog_factory('adhocracy', MercatorCatalogIndexes)
    config.add_indexview(index_location,
                         catalog_name='adhocracy',
                         index_name='mercator_location',
                         context=IMercatorSubResources)
    config.add_indexview(index_requested_funding,
                         catalog_name='adhocracy',
                         index_name='mercator_requested_funding',
                         context=IMercatorSubResources)
    config.add_indexview(index_budget,
                         catalog_name='adhocracy',
                         index_name='mercator_budget',
                         context=IMercatorSubResources)
    # this prevent an "AttributeError: 'module' object has no attribute
    # 'mercator2'" error when executing polytester
    import adhocracy_mercator.sheets.mercator2  # noqa
    config.add_indexview(mercator2_index_location,
                         catalog_name='adhocracy',
                         index_name='mercator_location',
                         context=sheets.mercator2.ILocation)
    config.add_indexview(mercator2_index_requested_funding,
                         catalog_name='adhocracy',
                         index_name='mercator_requested_funding',
                         context=sheets.mercator2.IFinancialPlanning)
    config.add_indexview(mercator2_index_budget,
                         catalog_name='adhocracy',
                         index_name='mercator_budget',
                         context=sheets.mercator2.IFinancialPlanning)
    config.add_indexview(mercator2_index_topic,
                         catalog_name='adhocracy',
                         index_name='mercator_topic',
                         context=sheets.mercator2.ITopic)
