"""Proposal resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItem
from adhocracy_sample.resources.section import ISection
from adhocracy_sample.resources.paragraph import IParagraph
from adhocracy.resources import ResourceFactory
from substanced.content import add_content_type
from zope.interface import taggedValue


class IProposalVersion(IItemVersion):

    """Versionable item with Document propertysheet."""

    taggedValue('extended_sheets',
                {'adhocracy.sheets.document.IDocument'})


class IProposal(IItem):

    """All versions of a Proposal."""

    taggedValue('element_types', {ITag, ISection, IParagraph, IProposalVersion})
    taggedValue('item_type', IProposalVersion)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    ifaces = [IProposalVersion, IProposal]
    for iface in ifaces:
        name = iface.queryTaggedValue('content_name') or iface.__identifier__
        meta = {'content_name': name,
                'add_view': 'add_' + iface.__identifier__,
                }
        add_content_type(config, iface.__identifier__,
                         ResourceFactory(iface),
                         factory_type=iface.__identifier__, **meta)
