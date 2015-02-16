"""Configure search catalogs."""
from zope.interface import Interface
from substanced import catalog
from substanced.interfaces import IIndexingActionProcessor


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
    config.scan('.index')
    config.include('.adhocracy')
    config.include('.subscriber')
