"""Mercator proposal."""
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_metadata
from adhocracy_core.resources.item import item_metadata
from adhocracy_core.resources.comment import add_commentsservice
from adhocracy_core.resources.rate import add_ratesservice
from adhocracy_core.sheets.geo import IPoint
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.comment import ICommentable
import adhocracy_meinberlin.sheets.kiezkassen


class IProposalVersion(IItemVersion):

    """A Kiezkasse proposal."""


proposal_version_meta = itemversion_metadata._replace(
    content_name='ProposalVersion',
    iresource=IProposalVersion,
    extended_sheets=[adhocracy_meinberlin.sheets.kiezkassen.IMain,
                     IPoint,
                     ICommentable,
                     IRateable],
    permission_add='add_kiezkassen_proposal_version',
)


class IProposal(IItem):

    """Kiezkasse proposal versions pool."""


proposal_meta = item_metadata._replace(
    content_name='Proposal',
    iresource=IProposal,
    element_types=[IProposalVersion],
    after_creation=item_metadata.after_creation + [
        add_commentsservice,
        add_ratesservice,
    ],
    item_type=IProposalVersion,
    is_implicit_addable=True,
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(proposal_version_meta, config)
