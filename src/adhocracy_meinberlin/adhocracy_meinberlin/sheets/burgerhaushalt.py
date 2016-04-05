"""Sheets for Burgerhaushalt proposals."""
from colander import drop
from colander import Range
from colander import Length
from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import SingleLine


class IProposal(ISheet):
    """Marker interface for Burgerhaushalt proposal sheet."""


class ProposalSchema(MappingSchema):
    """Data structure for the Burgerhaushalt information."""

    budget = CurrencyAmount(missing=drop,
                            default=None,
                            validator=Range(min=0))
    location_text = SingleLine(validator=Length(max=100))

proposal_meta = sheet_meta._replace(isheet=IProposal,
                                    schema_class=ProposalSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(proposal_meta, config.registry)
