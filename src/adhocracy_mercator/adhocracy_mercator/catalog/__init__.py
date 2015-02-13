""" Catalog utilities."""
from substanced.catalog import Keyword

from adhocracy_core.catalog.adhocracy import AdhocracyCatalogIndexes


class MercatorCatalogIndexes(AdhocracyCatalogIndexes):

    """Mercator indexes for the adhocracy catalog."""

    mercator_location = Keyword()
    mercator_requested_funding = Keyword()


def includeme(config):
    """Register catalog utilities."""
    config.add_catalog_factory('adhocracy', MercatorCatalogIndexes)
