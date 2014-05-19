"""Proposal resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItem
from adhocracy_sample.resources.section import ISection
from adhocracy_sample.resources.paragraph import IParagraph
from adhocracy.resources import add_resource_type_to_registry
from zope.interface import taggedValue


class IProposalVersion(IItemVersion):

    """Versionable item with Document propertysheet."""

    taggedValue('extended_sheets',
                set(['adhocracy.sheets.document.IDocument']))


class IProposal(IItem):

    """All versions of a Proposal."""

    taggedValue('element_types', set([ITag,
                                      ISection,
                                      IParagraph,
                                      IProposalVersion,
                                      ]))
    taggedValue('item_type', IProposalVersion)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    add_resource_type_to_registry(IProposalVersion, config)
    add_resource_type_to_registry(IProposal, config)
