"""Basic zodb persistent implementation for IResrouce."""
from persistent import Persistent
from zope.interface import implementer

from adhocracy_core.interfaces import resource_metadata
from adhocracy_core.interfaces import IResource
from adhocracy_core.utils import get_iresource
from adhocracy_core.utils import to_dotted_name


@implementer(IResource)
class Base(Persistent):

    """Persistent and location aware class."""

    __parent__ = None
    __name__ = None

    def __repr__(self):
        iface = get_iresource(self) or self.__class__
        iface_dotted = to_dotted_name(iface)
        oid = getattr(self, '__oid__', None)
        name = getattr(self, '__name__', None)
        identifier = str(oid)
        return '{0} oid: {1} name: {2}'.format(iface_dotted, identifier, name)


resource_metadata_defaults = resource_metadata._replace(
    iresource=IResource,
    content_class=Base,
    permission_add='add_resource',
    permission_view='view',
    after_creation=[],
)
