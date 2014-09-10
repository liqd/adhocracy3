"""Pool Sheet."""
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.sheets import GenericResourceSheet
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.schema import UniqueReferences


class PoolSheet(GenericResourceSheet):

    """Pool resource sheet."""

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

    elements = UniqueReferences(reftype=PoolElementsReference,
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
