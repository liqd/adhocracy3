"""Section resource type."""
from adhocracy.interfaces import IVersionableFubel
from adhocracy.interfaces import IFubelVersionsPool
from adhocracy.interfaces import ITag
from adhocracy.resources import ResourceFactory
from substanced.content import add_content_type
from zope.interface import taggedValue


class ISection(IVersionableFubel):

    """Document section."""

    taggedValue('extended_sheets', set(['adhocracy.sheets.document.ISection']))


class ISectionVersionsPool(IFubelVersionsPool):

    """Section Versions Pool."""

    taggedValue('addable_content_interfaces', set([ITag,
                                                   ISection]))
    taggedValue('fubel_type', ISection)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    ifaces = [ISection, ISectionVersionsPool]
    for iface in ifaces:
        name = iface.queryTaggedValue('content_name') or iface.__identifier__
        meta = {'content_name': name,
                'add_view': 'add_' + iface.__identifier__,
                }
        add_content_type(config, iface.__identifier__,
                         ResourceFactory(iface),
                         factory_type=iface.__identifier__, **meta)
