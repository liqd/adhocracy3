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

    def _get_reference_appstruct(self, params: dict={}) -> dict:
        if not params:
            return super()._get_reference_appstruct(params)
        local_params = params.copy()  # Local copy where we can delete elements
        raw_depth = local_params.pop('depth', '1')
        iface_filter = []
        append_if_not_none(iface_filter,
                           local_params.pop('content_type', None))
        append_if_not_none(iface_filter, local_params.pop('sheet', None))
        count_matching_elements = local_params.pop('count', False)
        elements_form = local_params.pop('elements', 'paths')
        local_params.pop('aggregateby', None)  # FIXME implement aggregateby
        if self._custom_filtering_necessary(raw_depth, iface_filter,
                                            count_matching_elements,
                                            elements_form, local_params):
            return self._build_filtered_appstruct(raw_depth, iface_filter,
                                                  count_matching_elements,
                                                  elements_form, local_params)
        else:
            return super()._get_reference_appstruct(params)

    def _custom_filtering_necessary(self, raw_depth: str,
                                    iface_filter: Iterable,
                                    count_matching_elements: bool,
                                    elements_form: str,
                                    remaining_params: dict):
        return (raw_depth != '1' or iface_filter or
                count_matching_elements or elements_form != 'paths' or
                remaining_params)

    def _build_filtered_appstruct(self, raw_depth: str, iface_filter: Iterable,
                                  count_matching_elements: bool,
                                  elements_form: str,
                                  remaining_params: dict):
        depth = None if raw_depth == 'all' else int(raw_depth)
        appstruct = {}
        elements = FormList(form=elements_form)
        for element in self._filter_elements(depth=depth,
                                             ifaces=iface_filter,
                                             valuefilters=remaining_params):
            elements.append(element)
        appstruct['elements'] = elements
        if count_matching_elements:
            appstruct['count'] = len(elements)
        return appstruct

    def _filter_elements(self, depth=1, ifaces: Iterable=None,
                         valuefilters: dict=None) -> Iterable:
        """See interface for docstring."""
        system_catalog = find_catalog(self.context, 'system')
        path_index = system_catalog['path']
        query = path_index.eq(resource_path(self.context), depth=depth,
                              include_origin=False)
        if ifaces:
            interface_index = system_catalog['interfaces']
            query &= interface_index.all(ifaces)
        if valuefilters:
            adhocracy_catalog = find_catalog(self.context, 'adhocracy')
            for name, value in valuefilters.items():
                # FIXME This will raise a KeyError if no such index exists.
                # Better validate first whether all remaining parameters
                # indicate existing catalogs and raise colander.Invalid
                # otherwise.
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
