"""Pool resource type."""
from adhocracy.interfaces import IPool
from adhocracy.resources import ResourceFactory
from substanced.content import add_content_type


class IBasicPool(IPool):

    """Basic Pool."""


def includeme(config):
    """Register resource type factory in substanced content registry."""
    ifaces = [IBasicPool]
    for iface in ifaces:
        name = iface.queryTaggedValue('content_name') or iface.__identifier__
        meta = {'content_name': name,
                'add_view': 'add_' + iface.__identifier__,
                }
        add_content_type(config, iface.__identifier__,
                         ResourceFactory(iface),
                         factory_type=iface.__identifier__, **meta)
