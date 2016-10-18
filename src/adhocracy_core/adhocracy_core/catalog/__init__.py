"""Configure search catalogs."""
from itertools import chain

from zope.interface import Interface
from pyramid.registry import Registry
from itertools import islice
from collections.abc import Iterable
from substanced import catalog
from substanced.interfaces import IIndexingActionProcessor
from substanced.catalog import CatalogsService
from substanced.catalog.indexes import AllowsComparator
from substanced.util import find_objectmap
from substanced.util import get_oid
from hypatia.interfaces import IIndex
from hypatia.interfaces import IResultSet
from hypatia.query import Query
from hypatia.util import ResultSet
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.interfaces import FieldComparator
from adhocracy_core.interfaces import FieldSequenceComparator
from adhocracy_core.interfaces import KeywordComparator
from adhocracy_core.interfaces import KeywordSequenceComparator
from adhocracy_core.interfaces import ReferenceComparator
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

    def reindex_all(self, resource: IResource):
        """Reindex `resource` with all indexes."""
        for value in self.values():
            value.reindex_resource(resource)

    def reindex_index(self, resource: IResource, index_name: str):
        """Reindex `resource` with index `index_name`.

        :raises KeyError: if `index_name`  index does not exists.
        """
        index = self.get_index(index_name)
        if index is None:
            msg = 'catalog index {0} does not exist.'.format(index_name)
            raise KeyError(msg)
        index.reindex_resource(resource)

    def search(self, query: SearchQuery) -> SearchResult:
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

    def _get_interfaces_index_query(self, query) -> Query:
        interfaces_value = self._get_query_value(query.interfaces)
        if not interfaces_value:
            return None
        interfaces_comparator = self._get_query_comparator(query.interfaces)
        interfaces_index = self.get_index('interfaces')
        if interfaces_comparator is None:
            interfaces_value = normalize_to_tuple(interfaces_value)
            index_query = interfaces_index.all(interfaces_value)
        else:
            index_comparator = getattr(interfaces_index, interfaces_comparator)
            index_query = index_comparator(interfaces_value)
        return index_query

    def _get_path_index_query(self, query) -> Query:
        if query.root is None:
            return None
        depth = query.depth or None
        path_index = self.get_index('path')
        return path_index.eq(query.root,
                             depth=depth,
                             include_origin=False)

    def _get_indexes_index_query(self, query) -> [Query]:
        if not query.indexes:
            return []
        indexes = []
        for index_name, value in query.indexes.items():
                index = self.get_index(index_name)
                comparator = self._get_query_comparator(value)
                if comparator is None:
                    index_comparator = index.eq
                else:
                    index_comparator = getattr(index, comparator)
                index_value = self._get_query_value(value)
                indexes.append(index_comparator(index_value))
        return indexes

    def _get_references_index_query(self, query) -> [Query]:
        indexes = []
        index = self.get_index('reference')
        for value in query.references:
            index_comparator = self._get_query_comparator(value)
            traverse = False
            if index_comparator == ReferenceComparator.traverse.value:
                traverse = True
            index_value = self._get_query_value(value)
            indexes.append(index.eq({'reference': index_value,
                                     'traverse': traverse}))
        return indexes

    def _get_private_visibility_index_query(self, query) -> Query:
        if not query.only_visible:
            return None
        visibility_index = self.get_index('private_visibility')
        return visibility_index.eq('visible')

    def _get_allowed_index_query(self, query) -> Query:
        if not query.allows:
            return None
        allowed_index = self.get_index('allowed')
        principals, permission = query.allows
        return allowed_index.allows(principals, permission)

    def _combine_indexes(self, query, *list_of_indexes) -> [Query]:
        maybes_indexes = chain.from_iterable(list_of_indexes)
        indexes = [idx for idx in maybes_indexes if idx is not None]
        return indexes

    def _execute_query(self, indexes) -> IResultSet:
        """Combine all query `indexes` with `&` and execute the query.

        If `indexes` is empty or it starts with a query from the `allows`
        index an empty result is returned. The allows index can only be used
        as a filter so you need a query that returns a search result first.
        """
        has_indexes = len(indexes) > 0
        is_starting_with_allows = has_indexes and isinstance(indexes[0],
                                                             AllowsComparator)
        if has_indexes and not is_starting_with_allows:
            index_query = indexes[0]
            for idx in indexes[1:]:
                index_query &= idx
            elements = index_query.execute(resolver=lambda x: x)
        else:
            elements = ResultSet(set(), 0, None)
        return elements

    def _search_elements(self, query) -> IResultSet:
        if not self.values():  # child catalogs/indexes are not created yet
            return ResultSet(set(), 0, None)
        indexes = self._combine_indexes(
            query,
            self._get_references_index_query(query),
            [self._get_path_index_query(query)],
            [self._get_interfaces_index_query(query)],
            self._get_indexes_index_query(query),
            [self._get_private_visibility_index_query(query)],
            [self._get_allowed_index_query(query)],)
        elements = self._execute_query(indexes)
        return elements

    def _get_frequency_of(self, elements: IResultSet,
                          query: SearchQuery) -> dict:
        frequency_of = {}
        if query.frequency_of:
            index = self.get_index(query.frequency_of)
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
            index = self.get_index(query.group_by)
            for value in index.unique_values():
                value_query = index.eq(value)
                value_elements = value_query.execute(resolver=None)
                intersect = elements.intersect(value_elements)
                if len(intersect) == 0:
                    continue
                group_by[value] = intersect
        sort_index = self.get_index(query.sort_by)
        if sort_index is not None and query.sort_by != 'reference':
            for key, intersect in group_by.items():
                intersect_sorted = intersect.sort(sort_index,
                                                  reverse=query.reverse,
                                                  limit=query.limit or None)
                group_by[key] = intersect_sorted
        for key, intersect in group_by.items():
            group_by[key] = self._resolve(intersect.all(), query)
        return group_by

    def _sort_elements(self, elements: IResultSet,
                       query: SearchQuery) -> IResultSet:
        if query.sort_by == '':
            pass
        elif query.sort_by == 'reference':
            if query.reverse:
                raise NotImplementedError()
            if query.limit:
                raise NotImplementedError()
            references = [x for x in query.references if x[0] is not None]
            if not references:  # we need at least one reference
                return elements
            reference = self._get_query_value(references[0])
            references_index = self.get_index('reference')
            elements_sorted = references_index.search_with_order(reference)
            elements = elements_sorted.intersect(elements)
        else:
            sort_index = self.get_index(query.sort_by)
            # TODO: We should assert the IIndexSort interface here, but
            # hypatia.field.FieldIndex is missing this interface.
            assert 'sort' in sort_index.__dir__()
            elements = elements.sort(sort_index,
                                     reverse=query.reverse)
        return elements

    def _get_slice(self, elements: Iterable, query: IResultSet) -> Iterable:
        """Get slice defined by `query.limit` and `query.offset`.

        :returns: Iterable or IResultSet if limit is not specified
        """
        elements_slice = elements
        if query.limit:
            elements_slice = islice(elements.all(resolve=None),
                                    query.offset,
                                    query.offset + query.limit)
        return elements_slice

    def _resolve(self, elements: [int], query: SearchQuery) -> Iterable:
        """Resolve oids from `elements`, convert to list if `query.resolve`."""
        objectmap = find_objectmap(self)
        elements = (objectmap.object_for(e) for e in elements)
        if query.resolve:
            elements = [x for x in elements]
        return elements

    def get_index(self, name) -> IIndex:
        system = self.get('system', {})
        adhocracy = self.get('adhocracy', {})
        index = system.get(name, None) or adhocracy.get(name, None)
        return index

    def _get_query_value(self, query_parameter: tuple) -> object:
        if self._is_tuple_starting_with_comparator(query_parameter):
            return query_parameter[1]
        else:
            return query_parameter

    def _get_query_comparator(self, query_parameter: tuple) -> object:
        if self._is_tuple_starting_with_comparator(query_parameter):
            return query_parameter[0]
        else:
            return

    def _is_tuple_starting_with_comparator(self, parameter: tuple) -> bool:
        if not isinstance(parameter, tuple):
            return False
        elif len(parameter) != 2:
            return False
        elif parameter[0] in self._comparators:
            return True
        else:
            return False

    def get_index_value(self, context: IResource, index_name: str):
        """Get value of index."""
        index = self.get_index(index_name)
        oid = get_oid(context)
        return index.document_repr(oid)

    _comparators = set(FieldComparator.__members__) \
        .union(KeywordComparator.__members__) \
        .union(KeywordSequenceComparator.__members__) \
        .union(FieldSequenceComparator.__members__) \
        .union(ReferenceComparator.__members__)


def add_catalogs_system_and_adhocracy(context: ICatalogsService,
                                      registry: Registry,
                                      options: dict):
    """Add catalogs `system` and `adhocracy`."""
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
    config.include('.system')
    config.include('.adhocracy')
    config.include('.subscriber')
