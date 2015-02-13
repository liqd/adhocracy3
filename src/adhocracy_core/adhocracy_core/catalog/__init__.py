"""Search / store indexed resources data."""
from substanced import catalog
from substanced.catalog.factories import IndexFactory
from substanced.interfaces import IIndexingActionProcessor
from zope.interface import Interface

from .index import ReferenceIndex


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
    """Register catalog utilities."""
    config.include('adhocracy_core.events')
    config.add_view_predicate('catalogable', catalog._CatalogablePredicate)
    config.add_directive('add_catalog_factory', catalog.add_catalog_factory)
    config.add_directive('add_indexview',
                         catalog.add_indexview,
                         action_wrap=False)
    config.registry.registerAdapter(catalog.deferred.BasicActionProcessor,
                                    (Interface,),
                                    IIndexingActionProcessor)
    config.scan('substanced.catalog')
    config.add_catalog_factory('adhocracy', AdhocracyCatalogIndexes)
    config.scan('adhocracy_core.catalog.index')
    config.include('.subscriber')
