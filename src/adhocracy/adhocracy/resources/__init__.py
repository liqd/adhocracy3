from zope.interface import directlyProvides
from zope.dottedname.resolve import resolve
from substanced.content import add_content_type
from adhocracy.resources import interfaces
from adhocracy.utils import (
    get_interfaces,
    get_taggedvalues,
)


class ResourceFactory:

    """Basic resource factory."""

    def __init__(self, iface):
        assert iface.isOrExtends(interfaces.IResource)
        taggedvalues = get_taggedvalues(iface)
        self.class_ = resolve(taggedvalues["content_class"])
        self.resource_iface = iface
        base_ifaces = taggedvalues["basic_properties_interfaces"]
        ext_ifaces = taggedvalues["extended_properties_interfaces"]
        self.prop_ifaces = [resolve(i) for i in base_ifaces.union(ext_ifaces)]

    def __call__(self, **kwargs):
        content = self.class_()
        directlyProvides(content, [self.resource_iface] + self.prop_ifaces)
        return content


# def includeme(config):
#
#     # iterate all Content interfaces
#     ifaces = get_interfaces(interfaces,
#                             base=interfaces.IContent,
#                             blacklist=[interfaces.IContentFolder, interfaces.IContentItem])
#     for iface in ifaces:
#         # register content types
#         is_implicit_addable = iface.queryTaggedValue("is_implicit_addable")
#         meta = {
#             "content_name": iface.queryTaggedValue("content_name") or iface.__identifier__,
#             "addable_content_interfaces": iface.queryTaggedValue("addable_content_interfaces") or [],
#             "is_implicit_addable": is_implicit_addable if is_implicit_addable is not None else True,
#             "add_view": "add_" + iface.__identifier__,
#             }
#         add_content_type(config, iface.__identifier__,
#                          ContentFactory(iface),
#                          factory_type=iface.__identifier__, **meta)
