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
from adhocracy.schema import ListOfUniqueReferences


class PoolSheet(GenericResourceSheet):

    """Pool resource sheet."""

    def filtered_elements(self, depth=1, ifaces: Iterable=None,
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
                index = adhocracy_catalog[name]
                query &= index.eq(value)
        resultset = query.execute()
        for result in resultset:
            yield result

    def _get_reference_appstruct(self):
        appstruct = {'elements': []}
        reftype = self._reference_nodes['elements'].reftype
        target_isheet = reftype.getTaggedValue('target_isheet')
        for child in self.context.values():
            if target_isheet.providedBy(child):
                appstruct['elements'].append(child)
        return appstruct


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

    elements = ListOfUniqueReferences(reftype=PoolElementsReference,
                                      readonly=True)


pool_metadata = sheet_metadata_defaults._replace(isheet=IPool,
                                                 schema_class=PoolSchema,
                                                 sheet_class=PoolSheet,
                                                 editable=False,
                                                 creatable=False,
                                                 )


def includeme(config):
    """Register adapter."""
    add_sheet_to_registry(pool_metadata, config.registry)
