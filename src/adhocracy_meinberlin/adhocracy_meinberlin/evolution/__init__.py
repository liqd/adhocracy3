"""Scripts to migrate legacy objects in existing databases."""
import logging  # pragma: no cover
from adhocracy_core.evolution import log_migration
from adhocracy_core.evolution import migrate_new_sheet
from adhocracy_meinberlin.resources.kiezkassen import IProposalVersion
import adhocracy_core.sheets
import adhocracy_meinberlin.sheets

logger = logging.getLogger(__name__)  # pragma: no cover


def use_adhocracy_core_title_sheet(root):  # pragma: no cover
    """Migrate kiezkassen proposal to adhocracy_core title sheet.

    Add title sheet.
    Remove title field from proposal sheet.
    """
    migrate_new_sheet(root, IProposalVersion,
                      adhocracy_core.sheets.title.ITitle,
                      adhocracy_meinberlin.sheets.kiezkassen.IProposal,
                      remove_isheet_old=False,
                      fields_mapping=[('title', 'title')])


def use_adhocracy_core_description_sheet(root):  # pragma: no cover
    """Migrate kiezkassen proposal to description sheet.

    Add description sheet.
    Remove detail field from proposal sheet.
    """
    migrate_new_sheet(root, IProposalVersion,
                      adhocracy_core.sheets.description.IDescription,
                      adhocracy_meinberlin.sheets.kiezkassen.IProposal,
                      remove_isheet_old=False,
                      fields_mapping=[('description', 'detail')])


@log_migration
def remove_meinberlin_workflow_assignment_sheets(root):  # pragma: no cover
    """Remove deprecated sheets.bplan/kiezkasse.IWorkflowAssignment."""
    from adhocracy_core.interfaces import IResource
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    from adhocracy_meinberlin import sheets
    migrate_new_sheet(root,
                      IResource,
                      IWorkflowAssignment,
                      sheets.bplan.IWorkflowAssignment,
                      remove_isheet_old=True,
                      )
    migrate_new_sheet(root,
                      IResource,
                      IWorkflowAssignment,
                      sheets.bplan.IPrivateWorkflowAssignment,
                      remove_isheet_old=True,
                      )
    migrate_new_sheet(root,
                      IResource,
                      IWorkflowAssignment,
                      sheets.kiezkassen.IWorkflowAssignment,
                      remove_isheet_old=True,
                      )


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(use_adhocracy_core_title_sheet)
    config.add_evolution_step(use_adhocracy_core_description_sheet)
    config.add_evolution_step(remove_meinberlin_workflow_assignment_sheets)
