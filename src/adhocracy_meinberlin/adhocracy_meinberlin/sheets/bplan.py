"""Sheets for BPlan proposals."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import workflow
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text


class IProposal(ISheet):

    """Marker interface for the BPlan proposal sheet."""


class ProposalSchema(colander.MappingSchema):

    """Data structure for plan stellungsname information."""

    name = SingleLine(missing=colander.required)
    street_number = SingleLine(missing=colander.required)
    postal_code_city = SingleLine(missing=colander.required)
    email = SingleLine(validator=colander.Email())
    statement = Text(missing=colander.required)


proposal_meta = sheet_meta._replace(isheet=IProposal,
                                    schema_class=ProposalSchema)


class IWorkflowAssignment(workflow.IWorkflowAssignment):

    """Marker interface for the bplan workflow assignment sheet."""


class WorkflowAssignmentSchema(workflow.WorkflowAssignmentSchema):

    """Data structure the bplan workflow assignment sheet."""

    workflow_name = 'bplan'

    draft = workflow.StateAssignment()
    announce = workflow.StateAssignment()
    participate = workflow.StateAssignment()
    evaluate = workflow.StateAssignment()
    closed = workflow.StateAssignment()


workflow_meta = workflow.workflow_meta._replace(
    isheet=IWorkflowAssignment,
    schema_class=WorkflowAssignmentSchema,
)


class IPrivateWorkflowAssignment(workflow.IWorkflowAssignment):

    """Marker interface for the bplan private workflow assignment sheet."""


class PrivateWorkflowAssignmentSchema(workflow.WorkflowAssignmentSchema):

    """Data structure the bplan private workflow assignment sheet."""

    workflow_name = 'bplan_private'


private_workflow_meta = workflow.workflow_meta._replace(
    isheet=IPrivateWorkflowAssignment,
    schema_class=PrivateWorkflowAssignmentSchema,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(proposal_meta, config.registry)
    add_sheet_to_registry(workflow_meta, config.registry)
    add_sheet_to_registry(private_workflow_meta, config.registry)
