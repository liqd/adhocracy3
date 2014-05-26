"""Name Sheet."""
import colander

from adhocracy.interfaces import ISheet
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.schema import Identifier


class IName(ISheet):

    """Market interface for the name sheet."""


class NameSchema(colander.MappingSchema):

    """Name sheet data structure.

    `name`: a human readable resource Identifier

    """

    name = Identifier(default='', missing=colander.drop)


name_metadata = sheet_metadata_defaults._replace(isheet=IName,
                                                 schema_class=NameSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(name_metadata, config.registry)
