"""Sheets for BPlan proposals."""
import colander

from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import workflow
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import Integer
from adhocracy_core.schema import Reference
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text
from adhocracy_core.sheets.principal import IUserBasic


class IProposal(ISheet):

    """Marker interface for the BPlan proposal sheet."""


class ProposalSchema(colander.MappingSchema):

    """Data structure for plan stellungsname information."""

    name = SingleLine(missing=colander.required)
    street_number = SingleLine(missing=colander.required)
    postal_code_city = SingleLine(missing=colander.required)
    email = SingleLine(validator=colander.Email())
    statement = Text(missing=colander.required,
                     validator=colander.Length(max=17500))


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
    frozen = workflow.StateAssignment()


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


class IProcessSettings(ISheet):

    """Marker interface for the ProcessSettings sheet."""


class OfficeWorkerUserReference(SheetToSheet):

    """OfficeWorker sheet User reference."""

    source_isheet = IProcessSettings
    source_isheet_field = 'office_worker'
    target_isheet = IUserBasic


class ProcessSettingsSchema(colander.MappingSchema):

    """Settings for the B-Plan process."""

    office_worker = Reference(reftype=OfficeWorkerUserReference)
    plan_number = Integer()
    participation_kind = SingleLine()
    participation_start_date = DateTime(default=None)
    participation_end_date = DateTime(default=None)

process_settings_meta = sheet_meta._replace(
    isheet=IProcessSettings,
    schema_class=ProcessSettingsSchema
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(proposal_meta, config.registry)
    add_sheet_to_registry(workflow_meta, config.registry)
    add_sheet_to_registry(private_workflow_meta, config.registry)
    add_sheet_to_registry(process_settings_meta, config.registry)
