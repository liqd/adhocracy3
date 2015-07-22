"""Sheets for digital leven process."""
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import workflow


class IWorkflowAssignment(workflow.IWorkflowAssignment):

    """Marker interface for the digital leben workflow assignment sheet."""


class WorkflowAssignmentSchema(workflow.WorkflowAssignmentSchema):

    """Data structure the digital_leben workflow assignment sheet."""

    workflow_name = 'digital_leben'

    draft = workflow.StateAssignment()
    participate = workflow.StateAssignment()
    evaluate = workflow.StateAssignment()
    result = workflow.StateAssignment()
    closed = workflow.StateAssignment()


workflow_meta = workflow.workflow_meta._replace(
    isheet=IWorkflowAssignment,
    schema_class=WorkflowAssignmentSchema,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(workflow_meta, config.registry)
