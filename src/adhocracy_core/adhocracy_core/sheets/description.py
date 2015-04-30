"""Description Sheet."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import Text


class IDescription(ISheet, ISheetReferenceAutoUpdateMarker):

    """Market interface for the description sheet."""


class DescriptionSchema(colander.MappingSchema):

    """Description sheet data structure.

    `description`: a description
    """

    description = Text()


description_meta = sheet_meta._replace(isheet=IDescription,
                                       schema_class=DescriptionSchema,
                                       )


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(description_meta, config.registry)
