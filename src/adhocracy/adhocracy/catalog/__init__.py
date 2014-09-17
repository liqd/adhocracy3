""" Catalog utilities."""
from substanced import catalog
from substanced.interfaces import IIndexingActionProcessor
from zope.interface import Interface

from .index import Reference


@catalog.catalog_factory('adhocracy')
class AdhocracyCatalogFactory:
    tag = catalog.Keyword()
    reference = Reference()


def includeme(config):
    """Register catalog utilities."""
    config.add_view_predicate('catalogable', catalog._CatalogablePredicate)
    config.add_directive('add_catalog_factory', catalog.add_catalog_factory)
    config.add_directive('add_indexview',
                         catalog.add_indexview,
                         action_wrap=False)
    config.registry.registerAdapter(catalog.deferred.BasicActionProcessor,
                                    (Interface,),
                                    IIndexingActionProcessor)
    config.scan('substanced.catalog')
    config.add_catalog_factory('adhocracy', AdhocracyCatalogFactory)
