from zope.interface import (
    implementer,
    directlyProvides
)
from zope.dottedname.resolve import resolve
from substanced.folder import Folder
from substanced.content import add_content_type
from adhocracy.contents import interfaces


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

    # register content types
    ifaces = []
    for key in dir(interfaces):
        value = getattr(interfaces, key)
        if value in [interfaces.IContent, interfaces.IContentFolder, interfaces.IContentItem]:
            continue
        try:
            if issubclass(value, interfaces.IContent):
                ifaces.append(value)
        except TypeError:
            continue
    for iface in ifaces:
        is_implicit_addable = iface.queryTaggedValue("is_implicit_addable")
        meta = {"content_name": iface.queryTaggedValue("content_name") or iface.__identifier__,
                "addable_content_interfaces": iface.queryTaggedValue("addable_content_interfaces") or [],
                "is_implicit_addable": is_implicit_addable if is_implicit_addable is not None else True,
                "add_view": "add_" + iface.__identifier__,
                }
        add_content_type(config, iface.__identifier__,
                         ContentFactory(iface),
                         factory_type=iface.__identifier__, **meta)
