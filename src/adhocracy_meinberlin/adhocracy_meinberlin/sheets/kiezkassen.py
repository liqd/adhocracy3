"""Sheets for Mercator proposals."""
from colander import Length
from colander import Range
from colander import required
from zope.deprecation import deprecated

from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import workflow
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import SingleLine


class IProposal(ISheet):
    """Marker interface for the Kiezkassen proposal sheet."""


class ProposalSchema(MappingSchema):
    """Data structure for organizational information."""

    # TODO: check exact length restrictions

    budget = CurrencyAmount(missing=required,
                            validator=Range(min=0, max=50000))
    creator_participate = Boolean()
    location_text = SingleLine(validator=Length(max=100))

proposal_meta = sheet_meta._replace(isheet=IProposal,
                                    schema_class=ProposalSchema)


class IWorkflowAssignment(workflow.IWorkflowAssignment):
    """Marker interface for the kiezkassen workflow assignment sheet."""


deprecated('IWorkflowAssignment',
           'Backward compatible code use IWorkflowAssignment instead')


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(proposal_meta, config.registry)
