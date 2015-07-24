"""Sheets for s1 process."""
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import workflow


class IWorkflowAssignment(workflow.IWorkflowAssignment):

    """Marker interface for the s1 process workflow assignment sheet."""


class WorkflowAssignmentSchema(workflow.WorkflowAssignmentSchema):

    """Data structure the s1 process workflow assignment sheet."""

    workflow_name = 's1'

    propose = workflow.StateAssignment()
    select = workflow.StateAssignment()
    result = workflow.StateAssignment()


workflow_meta = workflow.workflow_meta._replace(
    isheet=IWorkflowAssignment,
    schema_class=WorkflowAssignmentSchema,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(workflow_meta, config.registry)
