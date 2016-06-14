"""Scripts to migrate legacy objects in existing databases."""
from pyramid.registry import Registry
from adhocracy_core.interfaces import IPool
from adhocracy_core.evolution import migrate_new_sheet


def remove_likable_from_proposals(root: IPool,
                                  registry: Registry):  # pragma: no cover
    """Remove ILikable sheet from proposals."""
    from adhocracy_core.sheets.rate import IRateable
    from adhocracy_core.sheets.rate import ILikeable
    from adhocracy_s1.resources.s1 import IProposalVersion
    migrate_new_sheet(root, IProposalVersion, IRateable, ILikeable,
                      remove_isheet_old=True)


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(remove_likable_from_proposals)
