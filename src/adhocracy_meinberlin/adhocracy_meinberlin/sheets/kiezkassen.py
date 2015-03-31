"""Sheets for Mercator proposals."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_metadata_defaults
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text


class IMain(ISheet):

    """Marker interface for the Kiezkassen main sheet."""


class MainSchema(colander.MappingSchema):

    """Data structure for organizational information.

    FIXME: check exact length restrictions
    """

    title = SingleLine(validator=colander.Length(min=3, max=100))
    detail = Text(validator=colander.Length(max=500))
    budget = CurrencyAmount(
        missing=colander.required,
        validator=colander.Range(min=0, max=50000))
    creator_participate = Boolean()
    location_text = SingleLine(validator=colander.Length(max=100))


main_meta = sheet_metadata_defaults._replace(
    isheet=IMain, schema_class=MainSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(main_meta, config.registry)
