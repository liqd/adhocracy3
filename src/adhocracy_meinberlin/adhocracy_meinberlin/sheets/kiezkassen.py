"""Sheets for Mercator proposals."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text


class IProposal(ISheet):

    """Marker interface for the Kiezkassen proposal sheet."""


class ProposalSchema(colander.MappingSchema):

    """Data structure for organizational information."""

    # TODO: check exact length restrictions

    title = SingleLine(validator=colander.Length(min=3, max=100))
    detail = Text(validator=colander.Length(max=500))
    budget = CurrencyAmount(missing=colander.required,
                            validator=colander.Range(min=0, max=50000))
    creator_participate = Boolean()
    location_text = SingleLine(validator=colander.Length(max=100))


proposal_meta = sheet_meta._replace(isheet=IProposal,
                                    schema_class=ProposalSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(proposal_meta, config.registry)
