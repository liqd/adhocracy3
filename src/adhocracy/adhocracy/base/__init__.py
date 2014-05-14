"""Basic class for resources."""
from persistent import Persistent
from zope.interface import implementer

from pyramid.interfaces import ILocation
from adhocracy.utils import get_resource_interface
from adhocracy.utils import to_dotted_name


@implementer(ILocation)
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
