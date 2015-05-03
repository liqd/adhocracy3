"""Configure search catalogs."""
from zope.interface import Interface
from pyramid.registry import Registry
from itertools import islice
from collections.abc import Iterable
from substanced import catalog
from substanced.interfaces import IIndexingActionProcessor
from substanced.catalog import CatalogsService
from hypatia.interfaces import IIndex
from hypatia.interfaces import IResultSet
from hypatia.util import ResultSet
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.interfaces import SearchResult
from adhocracy_core.interfaces import SearchQuery
from adhocracy_core.interfaces import search_result
from adhocracy_core.interfaces import IResource
from adhocracy_core.resources.service import service_meta
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.utils import normalize_to_tuple



class ICatalogsService(IServicePool):

    """The 'catalogs' ServicePool."""


class CatalogsServiceAdhocracy(CatalogsService):

    def search(self, query: SearchQuery) -> SearchResult:  # flake8: noqa
        """Search indexes in catalogs `adhocracy` and `system`."""
        elements = self._search_elements(query)
        frequency_of = self._get_frequency_of(elements, query)
        group_by = self._get_group_by(elements, query)
        sorted_elements = self._sort_elements(elements, query)
        count = len(sorted_elements)
        elements_slice = self._get_slice(sorted_elements, query)
        resolved = self._resolve(elements_slice, query)
        result = search_result._replace(elements=resolved,
                                        count=count,
                                        group_by=group_by,
                                        frequency_of=frequency_of)
        return result

    def _search_elements(self, query) -> IResultSet:
        interfaces = normalize_to_tuple(query.interfaces)
        if not interfaces:
            interfaces = (IResource,)
        interfaces_index = self._get_index('interfaces')
        if interfaces_index is None:  # pragma: no branch
            return ResultSet(set(), 0, None)
        index_query = interfaces_index.all(interfaces)
        if query.root is not None:
            depth = query.depth or None
            path_index = self._get_index('path')
            index_query &= path_index.eq(query.root,
                                         depth=depth,
                                         include_origin=False)
        if query.arbitrary_indexes:
            for name, value in query.arbitrary_indexes.items():
                index = self._get_index(name)
                index_query &= index.eq(value)
        if query.references:
            index = self._get_index('reference')
            for reference in query.references:
                index_query &= index.eq(reference)
        if query.only_visible:
            visibility_index = self._get_index('private_visibility')
            index_query &= visibility_index.eq('visible')
        if query.allows:
            allowed_index = self._get_index('allowed')
            principals, permission = query.allows
            index_query &= allowed_index.allows(principals, permission)

        elements = index_query.execute(resolver=None)
        return elements

    def _get_frequency_of(self, elements: IResultSet,
                          query: SearchQuery) -> dict:
        frequency_of = {}
        if query.frequency_of:
            index = self._get_index(query.frequency_of)
            for value in index.unique_values():
                value_query = index.eq(value)
                value_elements = value_query.execute(resolver=None)
                intersect = elements.intersect(value_elements)
                count = len(intersect)
                if count == 0:
                    continue
                frequency_of[value] = count
        return frequency_of

    def _get_group_by(self, elements: IResultSet, query: SearchQuery) -> dict:
        group_by = {}
        if query.group_by:
            index = self._get_index(query.group_by)
            for value in index.unique_values():
                value_query = index.eq(value)
                value_elements = value_query.execute(resolver=None)
                intersect = elements.intersect(value_elements)
                if len(intersect) == 0:
                    continue
                group_by[value] = intersect
        sort_index = self._get_index(query.sort_by)
        if sort_index is not None:
            for key, intersect in group_by.items():
                intersect_sorted = intersect.sort(sort_index,
                                                  reverse=query.reverse,
                                                  limit=query.limit or None)
                group_by[key] = intersect_sorted
        if query.resolve:
            for key, intersect in group_by.items():
                intersect_resolved = [x for x in intersect]
                group_by[key] = intersect_resolved
        return group_by

    def _sort_elements(self, elements: IResultSet,
                       query: SearchQuery) -> IResultSet:
        sort_index = self._get_index(query.sort_by)
        if sort_index is not None:
            # TODO: We should assert the IIndexSort interfaces here, but
            # hypation.field.FieldIndex is missing this interfaces.
            assert 'sort' in sort_index.__dir__()
            elements = elements.sort(sort_index,
                                     reverse=query.reverse,
                                     limit=query.limit or None)
        return elements

    def _get_slice(self, elements: IResultSet, query: IResultSet) -> Iterable:
        """Get slice defined by `query.limit` and `query.offset`.

        :returns: IResultSet if not `query.limit`, else [IResource]
        """
        elements_slice = elements
        if query.limit:
            docids_slice = islice(elements.all(resolve=None),
                                  query.offset,
                                  query.offset + query.limit)
            elements_slice = [elements.resolver(x) for x in docids_slice]
        return elements_slice

    def _resolve(self, elements: Iterable, query: SearchQuery) -> Iterable:
        if query.resolve:
            elements = [x for x in elements]
        return elements

    def _get_index(self, name) -> IIndex:
        system = self.get('system', {})
        adhocracy = self.get('adhocracy', {})
        index = system.get(name, None) or adhocracy.get(name, None)
        return index


def add_catalogs_system_and_adhocracy(context: ICatalogsService,
                                      registry: Registry,
                                      options: dict):
    """Add catalogs 'system' and 'adhocracy'."""
    context.add_catalog('system')
    context.add_catalog('adhocracy')


catalogs_service_meta = service_meta._replace(
    iresource=ICatalogsService,
    content_name='catalogs',
    content_class=CatalogsServiceAdhocracy,
    after_creation=[add_catalogs_system_and_adhocracy]
)


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
    add_resource_type_to_registry(catalogs_service_meta, config)
    config.scan('substanced.catalog')
    config.scan('.index')
    config.include('.adhocracy')
    config.include('.subscriber')
