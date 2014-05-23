"""Proposal resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItem
from adhocracy_sample.resources.section import ISection
from adhocracy_sample.resources.paragraph import IParagraph
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.itemversion import itemversion_meta_defaults
from adhocracy.resources.item import item_meta_defaults

import adhocracy.sheets.document


class IProposalVersion(IItemVersion):

    """Versionable item with Document propertysheet."""


proposalversion_meta = itemversion_meta_defaults._replace(
    content_name='ProposalVersion',
    iresource=IProposalVersion,
    extended_sheets=[adhocracy.sheets.document.IDocument,
                     ],
)


class IProposal(IItem):

    """All versions of a Proposal."""


proposal_meta = item_meta_defaults._replace(
    content_name='Proposal',
    iresource=IProposal,
    element_types=[ITag,
                   ISection,
                   IParagraph,
                   IProposalVersion,
                   ],
    item_type=IProposalVersion,
)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    add_resource_type_to_registry(IProposalVersion, config)
    add_resource_type_to_registry(IProposal, config)
