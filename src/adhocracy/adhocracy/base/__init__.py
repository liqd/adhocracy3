"""Basic class for resources."""
from persistent import Persistent
from zope.interface import implementer

from pyramid.interfaces import ILocation
from adhocracy.utils import get_resource_interface


@implementer(ILocation)
class Base(Persistent):

    """Persistent and location aware class."""

    __parent__ = None
    __name__ = None

    def __str__(self):
        iresource = get_resource_interface(self) or ILocation
        iresource_str = iresource.__identifier__
        repr_str = repr(self)
        oid = getattr(self, '__oid__', '')
        id_str = str(oid) if oid else repr_str
        return '{0}:{1}'.format(iresource_str, id_str)
