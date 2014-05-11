"""Paragraph resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.interfaces import ITag
from adhocracy.resources import ResourceFactory
from substanced.content import add_content_type
from zope.interface import taggedValue


class IParagraphVersion(IItemVersion):

    """Document paragraph (a leaf in the section tree)."""

    taggedValue('extended_sheets',
                {'adhocracy.sheets.document.IParagraph'})


class IParagraph(IItem):

    """Paragraph Versions Pool."""

    taggedValue('element_types', {ITag, IParagraphVersion})
    taggedValue('item_type', IParagraphVersion)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    ifaces = [IParagraphVersion, IParagraph]
    for iface in ifaces:
        name = iface.queryTaggedValue('content_name') or iface.__identifier__
        meta = {'content_name': name,
                'add_view': 'add_' + iface.__identifier__,
                }
        add_content_type(config, iface.__identifier__,
                         ResourceFactory(iface),
                         factory_type=iface.__identifier__, **meta)
