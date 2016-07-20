"""Scripts to migrate legacy objects in existing databases."""
from pyramid.registry import Registry
from adhocracy_core.interfaces import IPool
from adhocracy_core.evolution import migrate_new_sheet
from adhocracy_core.evolution import log_migration
from adhocracy_core.workflows import update_workflow_state_acls


def remove_likable_from_proposals(root: IPool,
                                  registry: Registry):  # pragma: no cover
    """Remove ILikable sheet from proposals."""
    from adhocracy_core.sheets.rate import IRateable
    from adhocracy_core.sheets.rate import ILikeable
    from adhocracy_s1.resources.s1 import IProposalVersion
    migrate_new_sheet(root, IProposalVersion, IRateable, ILikeable,
                      remove_isheet_old=True)


@log_migration
def update_workflow_state_acl_for_all_resources(root,
                                                registry):  # pragma: no cover
    """Update the local :term:`acl` with the current workflow state acl."""
    update_workflow_state_acls(root, registry)


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(remove_likable_from_proposals)
    config.add_evolution_step(update_workflow_state_acl_for_all_resources)
