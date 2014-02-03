"""Proposal resource type."""
from adhocracy.interfaces import IVersionableFubel
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IFubelVersionsPool
from adhocracy.resources.section import ISectionVersionsPool
from adhocracy.resources import ResourceFactory
from substanced.content import add_content_type
from zope.interface import taggedValue


class IProposal(IVersionableFubel):

    """Versionable Fubel with Document propertysheet."""

    taggedValue('extended_sheets',
                set(['adhocracy.sheets.document.IDocument']))


class IProposalVersionsPool(IFubelVersionsPool):

    """Proposal Versions Pool."""

    taggedValue('addable_content_interfaces', set([ITag,
                                                   ISectionVersionsPool,
                                                   IProposal,
                                                   ]))
    taggedValue('fubel_type', IProposal)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    ifaces = [IProposal, IProposalVersionsPool]
    for iface in ifaces:
        name = iface.queryTaggedValue('content_name') or iface.__identifier__
        meta = {'content_name': name,
                'add_view': 'add_' + iface.__identifier__,
                }
        add_content_type(config, iface.__identifier__,
                         ResourceFactory(iface),
                         factory_type=iface.__identifier__, **meta)
