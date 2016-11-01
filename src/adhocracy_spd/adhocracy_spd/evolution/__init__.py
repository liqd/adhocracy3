"""Scripts to migrate legacy objects in existing databases."""
import logging  # pragma: no cover
from adhocracy_core.evolution import log_migration
from adhocracy_core.evolution import migrate_new_sheet


logger = logging.getLogger(__name__)  # pragma: no cover


@log_migration
def remove_spd_workflow_assignment_sheet(root, registry):  # pragma: no cover
    """Remove deprecated sheets.digital_leben.IWorkflowAssignment interface."""
    from adhocracy_core.interfaces import IResource
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    from adhocracy_spd.sheets import digital_leben
    migrate_new_sheet(root,
                      IResource,
                      IWorkflowAssignment,
                      digital_leben.IWorkflowAssignment,
                      remove_isheet_old=True,
                      )


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(remove_spd_workflow_assignment_sheet)
