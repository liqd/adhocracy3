"""Resouce configuration and default factory."""
from adhocracy.interfaces import (
    IProperty,
    IResource,
)
from adhocracy.resources import interfaces
from adhocracy.utils import (
    get_ifaces_from_module,
    get_all_taggedvalues,
)
from substanced.content import add_content_type
from zope.dottedname.resolve import resolve
from zope.interface import (
    directlyProvides,
    alsoProvides,
)


class ResourceFactory(object):

    """Basic resource factory."""

    def __init__(self, iface):
        assert iface.isOrExtends(IResource)
        taggedvalues = get_all_taggedvalues(iface)
        self.class_ = resolve(taggedvalues['content_class'])
        self.resource_iface = iface
        base_ifaces = taggedvalues['basic_properties_interfaces']
        ext_ifaces = taggedvalues['extended_properties_interfaces']
        self.prop_ifaces = [resolve(i) for i in base_ifaces.union(ext_ifaces)]
        for i in self.prop_ifaces:
            assert i.isOrExtends(IProperty)
        self.after_creation = taggedvalues['after_creation']

    def __call__(self, **kwargs):
        content = self.class_()
        directlyProvides(content, self.resource_iface)
        alsoProvides(content, self.prop_ifaces)
        for call in self.after_creation:
            call(content, None)
        return content


def includeme(config):
    """Register factories in substanced content registry.

    Iterate all resource interfaces and automatically register factories.

    """
    ifaces = get_ifaces_from_module(interfaces,
                                    base=IResource)
    for iface in ifaces:
        name = iface.queryTaggedValue('content_name') or iface.__identifier__
        meta = {
            'content_name': name,
            'add_view': 'add_' + iface.__identifier__,
        }
        add_content_type(config, iface.__identifier__,
                         ResourceFactory(iface),
                         factory_type=iface.__identifier__, **meta)
