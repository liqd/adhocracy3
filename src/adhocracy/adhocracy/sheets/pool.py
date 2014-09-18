"""Pool Sheet."""
from collections.abc import Iterable

from pyramid.traversal import resource_path
from substanced.util import find_catalog
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.sheets import GenericResourceSheet
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.schema import UniqueReferences
from adhocracy.utils import append_if_not_none
from adhocracy.utils import FormList
from adhocracy.utils import remove_keys_from_dict


filtering_pool_default_filter = ['depth', 'content_type', 'sheet', 'elements',
                                 'count', 'aggregateby']


class PoolSheet(GenericResourceSheet):

    """Generic pool resource sheet."""

    def _get_reference_appstruct(self, params):
        appstruct = {'elements': []}
        reftype = self._reference_nodes['elements'].reftype
        target_isheet = reftype.getTaggedValue('target_isheet')
        for child in self.context.values():
            if target_isheet.providedBy(child):
                appstruct['elements'].append(child)
        return appstruct


class FilteringPoolSheet(PoolSheet):

    """Resource sheet that allows filtering and aggregating pools."""

    def _get_reference_appstruct(self, params):
        if not params or not self._custom_filtering_necessary(params):
            return super()._get_reference_appstruct(params)
        appstruct = {}
        depth = self._build_depth(params)
        iface_filter = self._build_iface_filter(params)
        arbitrary_filters = self._get_arbitrary_filters(params)
        elements = self._build_elements_form_list(params)
        elements.extend(self._filter_elements(depth,
                                              iface_filter,
                                              arbitrary_filters,
                                              ))
        appstruct['elements'] = elements
        if self._count_matching_elements(params):
            appstruct['count'] = len(elements)
        # FIXME implement aggregateby
        return appstruct

    def _custom_filtering_necessary(self, params: dict) -> bool:
        params_copy = params.copy()
        return params_copy.pop('depth', '1') != '1' or\
            params_copy.pope('elements', 'path') != 'path' or\
            params_copy != {}

    def _get_arbitrary_filters(self, params):
        return remove_keys_from_dict(params, filtering_pool_default_filter)

    def _build_iface_filter(self, params: dict) -> dict:
        iface_filter = []
        append_if_not_none(iface_filter, params.get('content_type', None))
        append_if_not_none(iface_filter, params.get('sheet', None))
        return iface_filter

    def _build_elements_form_list(self, param) -> FormList:
        elements_serialization_form = param.get('elements', 'path')
        return FormList(form=elements_serialization_form)

    def _build_depth(self, params) -> int:
        raw_depth = params.get('depth', '1')
        return None if raw_depth == 'all' else int(raw_depth)

    def _count_matching_elements(self, params) -> bool:
        return params.get('count', False)

    def _filter_elements(self, depth=1, ifaces: Iterable=None,
                         arbitrary_filters: dict=None) -> Iterable:
        """See interface for docstring."""
        system_catalog = find_catalog(self.context, 'system')
        path_index = system_catalog['path']
        query = path_index.eq(resource_path(self.context), depth=depth,
                              include_origin=False)
        if ifaces:
            interface_index = system_catalog['interfaces']
            query &= interface_index.all(ifaces)
        if arbitrary_filters:
            adhocracy_catalog = find_catalog(self.context, 'adhocracy')
            for name, value in valuefilters.items():
                # FIXME This will raise a KeyError if no such index exists.
                # Better validate first whether all remaining parameters
                # indicate existing catalogs and raise colander.Invalid
                # otherwise.
            for name, value in arbitrary_filters.items():
                index = adhocracy_catalog[name]
                query &= index.eq(value)
        resultset = query.execute()
        for result in resultset:
            yield result


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
                                readonly=True)
    count = colander.SchemaNode(colander.Integer(), default=colander.drop)


pool_metadata = sheet_metadata_defaults._replace(
    isheet=IPool,
    schema_class=PoolSchema,
    sheet_class=FilteringPoolSheet,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register adapter."""
    add_sheet_to_registry(pool_metadata, config.registry)
