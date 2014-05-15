"""Basic zodb persistent implementation for IResrouce."""
from persistent import Persistent
from zope.interface import implementer

from adhocracy.interfaces import resource_meta
from adhocracy.interfaces import IResource
from adhocracy.utils import get_resource_interface
from adhocracy.utils import to_dotted_name


@implementer(IResource)
class Base(Persistent):

    """Persistent and location aware class."""

    __parent__ = None
    __name__ = None

    def __repr__(self):
        interface = get_resource_interface(self) or self.__class__
        interface_dotted = to_dotted_name(interface)
        oid = getattr(self, '__oid__', None)
        identifier = str(oid)
        return '{0} oid: {1}'.format(interface_dotted, identifier)


resource_meta_defaults = resource_meta._replace(
    content_name=IResource.__identifier__,
    iresource=IResource,
    content_class=Base,
    permission_add='add',
    permission_view='view',
)
