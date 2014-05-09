"""Basic class for resources."""
from persistent import Persistent
from adhocracy.interfaces import IResource
from adhocracy.utils import get_resource_interface
from zope.interface import implementer


@implementer(IResource)
class Resource(Persistent):

    """Persistent and location aware class."""

    __parent__ = None
    __name__ = None

    def __str__(self):
        iresource = get_resource_interface(self) or IResource
        iresource_str = iresource.__identifier__
        repr_str = repr(self)
        oid = getattr(self, '__oid__', '')
        id_str = str(oid) if oid else repr_str
        return '{0}:{1}'.format(iresource_str, id_str)
