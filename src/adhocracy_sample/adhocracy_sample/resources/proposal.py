"""Proposal resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItem
from adhocracy_sample.resources.comment import IComment
from adhocracy_sample.resources.section import ISection
from adhocracy_sample.resources.paragraph import IParagraph
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.itemversion import itemversion_metadata
from adhocracy.resources.item import item_metadata

import adhocracy.sheets.document


class IProposalVersion(IItemVersion):

    """Versionable item with Document propertysheet."""


proposalversion_meta = itemversion_metadata._replace(
    content_name='ProposalVersion',
    iresource=IProposalVersion,
    extended_sheets=[adhocracy.sheets.document.IDocument,
                     ],
)


class IProposal(IItem):

    """All versions of a Proposal."""


proposal_meta = item_metadata._replace(
    content_name='Proposal',
    iresource=IProposal,
    element_types=[ITag,
                   ISection,
                   IParagraph,
                   IComment,
                   IProposalVersion,
                   ],
    item_type=IProposalVersion,
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(proposalversion_meta, config)
    add_resource_type_to_registry(proposal_meta, config)
