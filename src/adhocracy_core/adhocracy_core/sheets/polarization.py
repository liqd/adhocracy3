"""Polarization sheet."""
import colander

from adhocracy_core.sheets import sheet_meta
from adhocracy_core.interfaces import IPredicateSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import AdhocracySchemaNode


class IPolarizable(IPredicateSheet):

    """Marker interface for the polarization sheet."""


class Position(AdhocracySchemaNode):

    """Schema node for the side (pro or contra)."""

    schema_type = colander.String
    missing = colander.drop
    default = 'pro'
    validator = colander.OneOf(['pro', 'contra']),


class PolarizableSchema(colander.MappingSchema):

    """
    Polarizable sheet data structure.

    `position`: the position in the debate, 'pro' or 'contra'.
    """

    position = Position()


polarizable_meta = sheet_meta._replace(
    isheet=IPolarizable,
    schema_class=PolarizableSchema,
    editable=True,
    creatable=True,
    create_mandatory=True
)


def includeme(config):
    """Register sheets, adapters and index views."""
    add_sheet_to_registry(polarizable_meta, config.registry)
