"""Sheets for Mercator proposals."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import workflow
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text


class IProposal(ISheet):

    """Marker interface for the Kiezkassen proposal sheet."""


class ProposalSchema(colander.MappingSchema):

    """Data structure for organizational information."""

    # TODO: check exact length restrictions

    detail = Text(validator=colander.Length(max=500))
    budget = CurrencyAmount(missing=colander.required,
                            validator=colander.Range(min=0, max=50000))
    creator_participate = Boolean()
    location_text = SingleLine(validator=colander.Length(max=100))


proposal_meta = sheet_meta._replace(isheet=IProposal,
                                    schema_class=ProposalSchema)


class IWorkflowAssignment(workflow.IWorkflowAssignment):

    """Marker interface for the kiezkassen workflow assignment sheet."""


class WorkflowAssignmentSchema(workflow.WorkflowAssignmentSchema):

    """Data structure the kiezkassen workflow assignment sheet."""

    workflow_name = 'sample'  # FIXME add custom workflow

    announced = workflow.StateAssignment()
    """Optional data related to a workflow state.

    The field name has to match an existing state name.
    """

workflow_meta = workflow.workflow_meta._replace(
    isheet=IWorkflowAssignment,
    schema_class=WorkflowAssignmentSchema,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(proposal_meta, config.registry)
    add_sheet_to_registry(workflow_meta, config.registry)
