"""Sheets for BPlan proposals."""
from colander import required
from colander import Length
from zope.deprecation import deprecated

from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import workflow
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Email
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text
from adhocracy_core.sheets.principal import IUserBasic


class IProposal(ISheet):
    """Marker interface for the BPlan proposal sheet."""


class ProposalSchema(MappingSchema):
    """Data structure for plan stellungsname information."""

    name = SingleLine(missing=required)
    street_number = SingleLine(missing=required)
    postal_code_city = SingleLine(missing=required)
    email = Email()
    statement = Text(missing=required,
                     validator=Length(max=17500))


proposal_meta = sheet_meta._replace(isheet=IProposal,
                                    schema_class=ProposalSchema)


class IWorkflowAssignment(workflow.IWorkflowAssignment):
    """Marker interface for the bplan workflow assignment sheet."""


deprecated('IWorkflowAssignment',
           'Backward compatible code use IWorkflowAssignment instead')


class IPrivateWorkflowAssignment(workflow.IWorkflowAssignment):
    """Marker interface for the bplan private workflow assignment sheet."""


deprecated('IPrivateWorkflowAssignment',
           'Backward compatible code use IWorkflowAssignment instead')


class IProcessSettings(ISheet):
    """Marker interface for the ProcessSettings sheet."""


class OfficeWorkerUserReference(SheetToSheet):
    """OfficeWorker sheet User reference."""

    source_isheet = IProcessSettings
    source_isheet_field = 'office_worker'
    target_isheet = IUserBasic


deprecated('OfficeWorkerUserReference',
           'Office worker email is not stored via an user anymore')


class ProcessSettingsSchema(MappingSchema):
    """Settings for the B-Plan process."""

    plan_number = SingleLine(missing=required)
    participation_kind = SingleLine(missing=required)

process_settings_meta = sheet_meta._replace(
    isheet=IProcessSettings,
    schema_class=ProcessSettingsSchema,
    create_mandatory=True
)


class IProcessPrivateSettings(ISheet):
    """Marker interface for the process private settings."""


class ProcessPrivateSettingsSchema(MappingSchema):
    """Private Settings for the B-Plan process."""

    office_worker_email = Email(missing=required)


process_private_settings_meta = sheet_meta._replace(
    isheet=IProcessPrivateSettings,
    schema_class=ProcessPrivateSettingsSchema,
    permission_view='view_bplan_private_settings'
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(proposal_meta, config.registry)
    add_sheet_to_registry(process_settings_meta, config.registry)
    add_sheet_to_registry(process_private_settings_meta, config.registry)
