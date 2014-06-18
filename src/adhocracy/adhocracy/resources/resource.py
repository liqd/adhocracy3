"""Basic zodb persistent implementation for IResrouce."""
from persistent import Persistent
from pyramid.registry import Registry
from zope.interface import implementer

from adhocracy.interfaces import resource_metadata
from adhocracy.interfaces import IResource
from adhocracy.utils import get_iresource
from adhocracy.utils import to_dotted_name
from adhocracy.websockets.client import notify_ws_server_of_created_resource


def notify_resource_created(context: IResource, registry: Registry,
                            options: dict) -> None:
    """Notify listeners that a new resource has been created."""
    notify_ws_server_of_created_resource(context)


@implementer(IResource)
class Base(Persistent):

    """Persistent and location aware class."""

    __parent__ = None
    __name__ = None

    def __repr__(self):
        interface = get_iresource(self) or self.__class__
        interface_dotted = to_dotted_name(interface)
        oid = getattr(self, '__oid__', None)
        identifier = str(oid)
        return '{0} oid: {1}'.format(interface_dotted, identifier)


resource_metadata_defaults = resource_metadata._replace(
    content_name=IResource.__identifier__,
    iresource=IResource,
    content_class=Base,
    permission_add='add',
    permission_view='view',
    after_creation=[notify_resource_created],
)
