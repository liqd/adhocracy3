"""Mercator proposal."""
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_metadata
from adhocracy_core.resources.item import item_metadata
from adhocracy_core.resources.comment import add_commentsservice
from adhocracy_core.resources.rate import add_ratesservice
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.comment import ICommentable
import adhocracy_mercator.sheets.mercator


class IMercatorProposalVersion(IItemVersion):

    """A Mercator proposal."""


mercator_proposal_version_meta = itemversion_metadata._replace(
    content_name='MercatorProposalVersion',
    iresource=IMercatorProposalVersion,
    extended_sheets=[adhocracy_mercator.sheets.mercator.IUserInfo,
                     adhocracy_mercator.sheets.mercator.IOrganizationInfo,
                     adhocracy_mercator.sheets.mercator.IIntroduction,
                     adhocracy_mercator.sheets.mercator.IDetails,
                     adhocracy_mercator.sheets.mercator.IMotivation,
                     adhocracy_mercator.sheets.mercator.IFinance,
                     adhocracy_mercator.sheets.mercator.IExtras,
                     ICommentable,
                     IRateable],

)


class IMercatorProposal(IItem):

    """Mercator proposal versions pool."""


mercator_proposal_meta = item_metadata._replace(
    content_name='MercatorProposal',
    iresource=IMercatorProposal,
    element_types=[IMercatorProposalVersion,
                   ],
    after_creation=item_metadata.after_creation + [
        add_commentsservice,
        add_ratesservice,
    ],
    item_type=IMercatorProposalVersion,
    is_implicit_addable=True,
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(mercator_proposal_meta, config)
    add_resource_type_to_registry(mercator_proposal_version_meta, config)
