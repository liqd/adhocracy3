"""List, search and filter child resources."""
from copy import deepcopy
from collections.abc import Iterable
from collections import namedtuple
from itertools import islice

from pyramid.traversal import resource_path
from pyramid.util import DottedNameResolver
from substanced.util import find_catalog
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import AnnotationStorageSheet
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.utils import append_if_not_none
from adhocracy_core.utils import remove_keys_from_dict


dotted_name_resolver = DottedNameResolver()


filtering_pool_default_filter = ['depth', 'content_type', 'sheet', 'elements',
                                 'count', 'sort', 'reverse', 'limit', 'offset',
                                 'aggregateby', 'aggregateby_elements',
                                 ]


FilterElementsResult = namedtuple('FilterElementsResult',
                                  ['elements', 'count', 'aggregateby'])


class PoolSheet(AnnotationStorageSheet):

    """Generic pool resource sheet."""

    # TODO remove, this class is not used

    def _get_reference_appstruct(self, params):
        appstruct = {'elements': []}
        reftype = self._reference_nodes['elements'].reftype
        target_isheet = reftype.getTaggedValue('target_isheet')
        for child in self.context.values():
            if target_isheet.providedBy(child):
                appstruct['elements'].append(child)
        return appstruct


class FilteringPoolSheet(PoolSheet):

    """Pool resource sheet that allows filtering and aggregating elements."""

    def get(self, params: dict={}) -> dict:
        """Search for child resources.

        :param params: Query parameters to search / filter the
        returned references.
        The query data structure is specified in
        :class:`adhocracy_core.rest.schemas.GETPoolRequestSchema`
        For detailed usage information read :docs:`../../docs/rest_api`.
        Additional arbitrary filters are defined in
        :class:`adhocracy_core.catalog.adhocracy.AdhocracyCatalogIndexes`.

        If empty only direct child resources are returned and filtered by
        the target_isheet of the elements field.
        """
        return super().get(params)

    def _get_reference_appstruct(self, params: dict={}) -> dict:
        """Get appstruct with references according to `params` query."""
        serialization_form = params.get('elements', 'path')
        resolve_resources = False if serialization_form == 'omit' else True
        query = {'depth': self._build_depth(params),
                 'ifaces': self._build_iface_filter(params),
                 'arbitrary_filters': self._get_arbitrary_filters(params),
                 'resolve_resources': resolve_resources,
                 'references': self._get_reference_filters(params),
                 'sort_filter': params.get('sort', ''),
                 'reverse': params.get('reverse', False),
                 'limit': params.get('limit', None),
                 'offset': params.get('offset', 0),
                 'aggregate_filter': params.get('aggregateby', ''),
                 'aggregate_form': params.get('aggregateby_elements', 'count')
                 }
        result = self._filter_elements(**query)
        appstruct = {}
        if resolve_resources:
            appstruct['elements'] = list(result.elements)
        if params.get('count', False):
            appstruct['count'] = result.count
        if params.get('aggregateby', ''):
            appstruct['aggregateby'] = result.aggregateby
        return appstruct

    def _get_arbitrary_filters(self, params: dict) -> dict:
        filter = filtering_pool_default_filter
        reference_filters = self._get_reference_filters(params).keys()
        filter.extend(reference_filters)
        return remove_keys_from_dict(params, filter)

    def _get_reference_filters(self, params: dict) -> dict:
        filters = {}
        for key, value in params.items():
            if (':') in key:
                filters[key] = value
        return filters

    def _build_iface_filter(self, params: dict) -> dict:
        iface_filter = []
        append_if_not_none(iface_filter, params.get('content_type', None))
        append_if_not_none(iface_filter, params.get('sheet', None))
        if not iface_filter:
            # By default, filter by the target_isheet of elements
            reftype = self._reference_nodes['elements'].reftype
            iface_filter.append(reftype.getTaggedValue('target_isheet'))
        return iface_filter

    def _build_depth(self, params) -> int:
        raw_depth = params.get('depth', '1')
        return None if raw_depth == 'all' else int(raw_depth)

    def _filter_elements(self, depth=1, ifaces: Iterable=None,
                         arbitrary_filters: dict=None,
                         resolve_resources=True,
                         references: dict=None,
                         sort_filter: str='',
                         reverse: bool=False,
                         limit: int=None,
                         offset: int=0,
                         aggregate_filter: str=None,
                         aggregate_form: str='count',
                         ) -> FilterElementsResult:
        system_catalog = find_catalog(self.context, 'system')
        # filter path
        path_index = system_catalog['path']
        query = path_index.eq(resource_path(self.context), depth=depth,
                              include_origin=False)
        # filter ifaces
        if ifaces:
            interface_index = system_catalog['interfaces']
            query &= interface_index.all(ifaces)
        # filter arbitrary
        adhocracy_catalog = find_catalog(self.context, 'adhocracy')
        if arbitrary_filters:
            for name, value in arbitrary_filters.items():
                index = adhocracy_catalog[name]
                query &= index.eq(value)
        # filter references
        if references:
            index = adhocracy_catalog['reference']
            for name, value in references.items():
                isheet_name, isheet_field = name.split(':')
                isheet = dotted_name_resolver.resolve(isheet_name)
                query &= index.eq(isheet, isheet_field, value)
        # Only show visible elements (not hidden or deleted)
        visibility_index = adhocracy_catalog['private_visibility']
        query &= visibility_index.eq('visible')
        # Execute filter query
        identity = lambda x: x  # pragma: no branch
        resolver = None if resolve_resources else identity
        elements = query.execute(resolver=resolver)
        # Sort
        sort_index = system_catalog.get(sort_filter, None) \
            or adhocracy_catalog.get(sort_filter, None)
        if sort_index is not None:
            # TODO: We should assert the IIndexSort interfaces here, but
            # hypation.field.FieldIndex is missing this interfaces.
            assert 'sort' in sort_index.__dir__()
            elements = elements.sort(sort_index, reverse)
        # Count
        count = len(elements)
        # Limit with offset
        if limit is not None:
            elements = islice(elements.all(), offset, offset + limit)
        # Aggregate
        aggregateby = {}
        if aggregate_filter:
            aggregateby[aggregate_filter] = {}
            index = adhocracy_catalog.get(aggregate_filter, None)\
                or system_catalog.get(aggregate_filter)
            for value in index.unique_values():
                value_query = query & index.eq(value)
                if aggregate_form == 'count':
                    value_elements = len(value_query.execute(
                        resolver=identity))
                else:
                    # TODO do we really want to  destroy the generator here?
                    value_elements = list(value_query.execute(
                        resolver=None))
                if value_elements:
                    aggregateby[aggregate_filter][str(value)] = value_elements
        return FilterElementsResult(elements, count, aggregateby)

    def _get_schema_for_cstruct(self, request, params: dict):
        """Return extended schema to serialize cstruct.

        :param params: dictionary with optionally key 'elements' and
        value 'content'. If set do not serialize the references path only but
        the full resource cstruct.
        """
        schema = super()._get_schema_for_cstruct(request, params)
        if params.get('elements', None) == 'content':
            elements = schema['elements']
            typ_copy = deepcopy(elements.children[0].typ)
            typ_copy.serialization_form = 'content'
            elements.children[0].typ = typ_copy
        return schema


class IPool(ISheet):

    """Marker interface for the pool sheet."""


class PoolElementsReference(SheetToSheet):

    """Pool sheet elements reference."""

    source_isheet = IPool
    source_isheet_field = 'elements'
    target_isheet = ISheet


class PoolSchema(colander.MappingSchema):

    """Pool sheet data structure.

    `elements`: children of this resource (object hierarchy).
    """

    elements = UniqueReferences(reftype=PoolElementsReference,
                                readonly=True,
                                )

    def after_bind(self, node: colander.MappingSchema, kw: dict):
        request = kw.get('request', None)
        if request is None:
            return
        if request.validated.get('count', False):
            child = colander.SchemaNode(colander.Integer(),
                                        default=0,
                                        missing=colander.drop,
                                        name='count')
            node.add(child)
        if request.validated.get('aggregateby', ''):
            child = colander.SchemaNode(colander.Mapping(unknown='preserve'),
                                        default={},
                                        missing=colander.drop,
                                        name='aggregateby')
            node.add(child)


pool_meta = sheet_meta._replace(
    isheet=IPool,
    schema_class=PoolSchema,
    sheet_class=FilteringPoolSheet,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register adapter."""
    add_sheet_to_registry(pool_meta, config.registry)
