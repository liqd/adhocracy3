"""Scripts to migrate legacy objects in existing databases."""
import logging  # pragma: no cover
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


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(use_adhocracy_core_title_sheet)
