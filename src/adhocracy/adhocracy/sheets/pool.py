"""Pool Sheet."""
import colander
from pyramid.httpexceptions import HTTPNotImplemented

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.sheets import GenericResourceSheet
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.schema import ListOfUniqueReferences


class PoolSheet(GenericResourceSheet):

    """Pool resource sheet."""

    def get(self):
        """Get appstruct."""
        struct = super().get()
        elements = []
        reftype = self.schema['elements'].reftype
        target_isheet = reftype.getTaggedValue('target_isheet')
        for child in self.context.values():
            if target_isheet.providedBy(child):
                elements.append(child)
        struct['elements'] = elements
        return struct

    def set(self, struct, omit=()):
        """Store appstruct."""
        raise HTTPNotImplemented()

    def validate_cstruct(self, cstruct):
        """Return None."""
        raise HTTPNotImplemented()


class IPool(ISheet):

    """Marker interface for the pool sheet."""


class IPoolElementsReference(SheetToSheet):

    """Pool sheet elements reference."""

    source_isheet = IPool
    source_isheet_field = 'elements'
    target_isheet = ISheet


class PoolSchema(colander.MappingSchema):

    """Pool sheet data structure.

    `elements`: children of this resource (object hierarchy).

    """

    elements = ListOfUniqueReferences(reftype=IPoolElementsReference)


pool_metadata = sheet_metadata_defaults._replace(isheet=IPool,
                                                 schema_class=PoolSchema,
                                                 sheet_class=PoolSheet,
                                                 readonly=True)


def includeme(config):
    """Register adapter."""
    add_sheet_to_registry(pool_metadata, config.registry)
