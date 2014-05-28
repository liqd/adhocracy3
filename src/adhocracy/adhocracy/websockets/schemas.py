"""Colander schemas to validate and (de)serialize Websocket messages."""
import colander

from adhocracy.schema import ResourceObject


class Action(colander.SchemaNode):

    """An action requested by a client."""

    schema_type = colander.String
    validator = colander.OneOf(['subscribe', 'unsubscribe'])


class ClientRequestSchema(colander.MappingSchema):

    """Data structure for client requests."""

    action = Action()
    resource = colander.SchemaNode(ResourceObject())


class Status(colander.SchemaNode):

    """A status sent to the client."""

    schema_type = colander.String
    validator = colander.OneOf(['ok', 'duplicate'])
    default = 'ok'


class StatusConfirmation(ClientRequestSchema):

    """Data structure for status confirmations sent to the client."""

    status = Status()
