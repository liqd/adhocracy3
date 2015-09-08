"""Sheets for Burgerhaushalt proposals."""

import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import SingleLine


class IProposal(ISheet):

    """Marker interface for Burgerhaushalt proposal sheet."""


class ProposalSchema(colander.MappingSchema):

    """Data structure for the Burgerhaushalt information."""

    budget = CurrencyAmount(missing=colander.drop,
                            default=None,
                            validator=colander.Range(min=0))
    location_text = SingleLine(validator=colander.Length(max=100))

proposal_meta = sheet_meta._replace(isheet=IProposal,
                                    schema_class=ProposalSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(proposal_meta, config.registry)
