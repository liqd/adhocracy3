from zope.interface import (
    directlyProvides
)
from zope.dottedname.resolve import resolve
from substanced.content import add_content_type
from adhocracy.resources import interfaces
from adhocracy.utils import get_interfaces

# basic factory
class ContentFactory:

    def __init__(self, iface):
        # default
        self.main_iface = iface
        self.addit_ifaces = [resolve(i) for i in (iface.queryTaggedValue("propertysheet_interfaces") or [])]
        self.base_class = resolve(iface.getTaggedValue("content_class"))
        self.base_class_kwargs = {}

    def __call__(self, **kwargs):
        content = self.base_class(**self.base_class_kwargs)
        directlyProvides(content, [self.main_iface] + self.addit_ifaces)
        return content


def includeme(config):

    # iterate all Content interfaces
    ifaces = get_interfaces(interfaces,
                            base=interfaces.IContent,
                            blacklist=[interfaces.IContentFolder, interfaces.IContentItem])
    for iface in ifaces:
        # register content types
        is_implicit_addable = iface.queryTaggedValue("is_implicit_addable")
        meta = {"content_name": iface.queryTaggedValue("content_name") or iface.__identifier__,
                "addable_content_interfaces": iface.queryTaggedValue("addable_content_interfaces") or [],
                "is_implicit_addable": is_implicit_addable if is_implicit_addable is not None else True,
                "add_view": "add_" + iface.__identifier__,
                }
        add_content_type(config, iface.__identifier__,
                         ContentFactory(iface),
                         factory_type=iface.__identifier__, **meta)
