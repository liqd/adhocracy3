"""Adhocracy catalog and index views."""
from substanced import catalog
from substanced.catalog import IndexFactory
from adhocracy_core.catalog.index import ReferenceIndex

# TODO move index views here


class Reference(IndexFactory):
    index_type = ReferenceIndex


class AdhocracyCatalogIndexes:

    """Default indexes for the adhocracy catalog.

    Indexes starting with `private_` are private (not queryable from the
    frontend).
    """

    tag = catalog.Keyword()
    private_visibility = catalog.Keyword()  # visible / deleted / hidden
    rate = catalog.Field()
    rates = catalog.Field()
    creator = catalog.Field()
    reference = Reference()


def includeme(config):
    """Register adhocracy catalog factory."""
    config.add_catalog_factory('adhocracy', AdhocracyCatalogIndexes)
