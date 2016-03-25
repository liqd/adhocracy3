"""Title Sheet."""
from colander import Length

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import SingleLine


class ITitle(ISheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for the title sheet."""


class TitleSchema(MappingSchema):
    """Title sheet data structure.

    `title`: a human readable title
    """

    title = SingleLine(validator=Length(min=3, max=200))


title_meta = sheet_meta._replace(isheet=ITitle,
                                 schema_class=TitleSchema,
                                 )


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(title_meta, config.registry)
