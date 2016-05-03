"""Colander schemas to validate and (de)serialize Websocket messages."""
from colander import OneOf
from colander import required
from colander import deferred
from colander import Invalid
from pyramid.traversal import resource_path

from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import ResourceObjectType
from adhocracy_core.schema import Resource
from adhocracy_core.schema import SchemaNode


class Action(SingleLine):
    """An action requested by a client."""

    validator = OneOf(['subscribe', 'unsubscribe'])


class SubscribableResource(Resource):  # pragma: no cover
    """Temporary fix for #2244.

    TODO: implement proper solution
    """

    missing = required

    @deferred
    def validator(self, kw: dict) -> callable:
        """Check that unauthorized paths are not used."""
        def avalidator(node, cstruct):
            path = resource_path(cstruct)
            forbidden_paths = ['/principals', '/catalogs']
            for forbidden in forbidden_paths:
                if path.startswith(forbidden):
                    raise Invalid(node, 'Unauthorized path subscription: {}'.
                                  format(forbidden))

        return avalidator


class ClientRequestSchema(MappingSchema):
    """Data structure for client requests."""

    action = Action(missing=required)
    resource = SubscribableResource()


class Status(SingleLine):
    """A status sent to the client."""

    validator = OneOf(['ok', 'redundant'])
    default = 'ok'


class StatusConfirmation(ClientRequestSchema):
    """Data structure for status confirmations sent to the client."""

    status = Status()


class Event(SingleLine):
    """The type of event notifications sent to the client."""

    validator = OneOf(['modified',            # Used internally
                       'removed',             # and for
                       'changed_descendants',  # the client
                       'new_child',
                       'removed_child',
                       'modified_child',
                       'new_version',
                       'created'])   # Only used internally
    default = 'modified'


class ServerNotification(MappingSchema):
    """Notification sent to the server from the Pyramid WS client."""

    event = Event()
    resource = SchemaNode(ResourceObjectType(serialization_form='path'))


class Notification(MappingSchema):
    """Notification sent to a client if a resource has changed."""

    event = Event()
    resource = Resource()


class ChildNotification(Notification):
    """ServerNotification involving a child resource."""

    child = Resource()


class VersionNotification(Notification):
    """ServerNotification involving a version."""

    version = Resource()
