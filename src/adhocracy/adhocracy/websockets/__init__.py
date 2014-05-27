"""Asynchronous client-server communication via Websockets."""
from collections import defaultdict
from collections.abc import Iterable
from json import dumps
from json import loads
from logging import getLogger

from autobahn.asyncio.websocket import WebSocketServerProtocol
from autobahn.websocket.protocol import ConnectionRequest
from substanced.util import get_oid
import colander

from adhocracy.interfaces import IResource
from adhocracy.schema import ResourceObject


logger = getLogger(__name__)


class WebSocketError(Exception):

    """An error that occurs during communication with a WebSocket client."""

    def __init__(self, error_type: str, details: str):
        self.error_type = error_type
        self.details = details

    def __str__(self):
        return '{}: {}'.format(self.error_type, self.details)


class Action(colander.SchemaNode):

    """An action requested by a client."""

    schema_type = colander.String
    validator = colander.OneOf(['subscribe', 'unsubscribe'])


class ClientRequestSchema(colander.MappingSchema):

    """Data structure for client requests."""

    action = Action()

    resource = colander.SchemaNode(ResourceObject())


class ClientTracker():

    """"Keeps track of the clients that want notifications."""

    def __init__(self):
        """Create a new instance."""
        self._clients2resource_oids = defaultdict(set)
        self._resource_oids2clients = defaultdict(set)

    def is_subscribed(self, client: str, resource: IResource) -> bool:
        """Check whether a client is subscribed to a resource."""
        oid = get_oid(resource)
        return (client in self._clients2resource_oids and
                oid in self._clients2resource_oids[client])

    def subscribe(self, client: str, resource: IResource) -> bool:
        """Subscribe a client to a resource, if necessary.

        Returns True if the subscription was successful, False if it was
        unnecessary (the client was already subscribed).

        If the client is already subscribed, this method is a no-op.

        """
        if self.is_subscribed(client, resource):
            return False
        oid = get_oid(resource)
        self._clients2resource_oids[client].add(oid)
        self._resource_oids2clients[oid].add(client)
        return True

    def unsubscribe(self, client: str, resource: IResource) -> bool:
        """Unsubscribe a client from a resource, if necessary.

        Returns True if the unsubscription was successful, False if it was
        unnecessary (the client was not subscribed).

        """
        if not self.is_subscribed(client, resource):
            return False
        oid = get_oid(resource)
        self._discard_from_multidict(self._clients2resource_oids, client, oid)
        self._discard_from_multidict(self._resource_oids2clients, oid, client)
        return True

    def _discard_from_multidict(self, multidict, key, value):
        """Discard one set member from a defaultdict that has sets as values.

        If the resulting set is empty, it is removed from the multidict.

        """
        if key in multidict:
            multidict[key].discard(value)
            if not multidict[key]:
                del multidict[key]

    def delete_all_subscriptions(self, client: str) -> None:
        """Delete all subscriptions for a client."""
        oid_set = self._clients2resource_oids.pop(client, set())
        for oid in oid_set:
            self._discard_from_multidict(self._resource_oids2clients, oid,
                                         client)

    def iterate_subscribers(self, resource: IResource) -> Iterable:
        """Return an iterator over all clients subscribed to a resource."""
        oid = get_oid(resource)
        # 'if' check is necessary to avoid creating spurious empty sets
        if oid in self._resource_oids2clients:
            for client in self._resource_oids2clients[oid]:
                yield client


class ClientCommunicator(WebSocketServerProtocol):

    """Communicates with a client through a WebSocket connection."""

    # All instances of this class share the same tracker
    tracker = ClientTracker()

    def __init__(self, context):
        """Create a new instance."""
        self._client_request_schema = ClientRequestSchema()
        self._client_request_schema.bind(context=context)

    def onConnect(self, request: ConnectionRequest):
        self._client = request.peer
        logger.debug('Client connecting: %s', self._client)

    def onOpen(self):
        logger.debug('WebSocket connection to %s open', self._client)

    def onMessage(self, payload: bytes, is_binary: bool) -> None:
        json_object = self._parse_message(payload, is_binary)
        request = self._convert_json_into_client_request(json_object)

        # TODO handle_client_request -- throw subscribe_not_supported if an
        # ItemVersion

        # TODO convert everything into a WebSocketError
        # TODO handle message and send suitable response
        # TODO check that result is dict

    def _parse_message(self, payload: bytes, is_binary: bool) -> object:
        """Parse a client message into a JSON object.

        :raise WebSocketError: if the message doesn't contain UTF-8 encoded
                               text or cannot be parsed as JSON

        """
        if is_binary:
            raise WebSocketError('malformed_message', 'message is binary')
        try:
            text = payload.decode()
            logger.debug('Received text message from client %s: %s',
                         self._client, text)
            return loads(text)
        except ValueError as err:
            raise WebSocketError('malformed_message', err.args[0])

    def _convert_json_into_client_request(self, json_object):
        try:
            return self._client_request_schema.deserialize(json_object)
        except colander.Invalid as err:
            details = ' / '.join(err.messages())
            raise WebSocketError('invalid_json', details)
            # TODO 'unknown_action' and 'unknown_resource' should be reported
            # as distinct error types: check whether err.asdict() has 'action'
            # or 'resource' key (provided the field actually exists and is a
            # string; as long as it's the only error

    def _send_error_message(self, error: str, details: str) -> None:
        # TODO serialize WebSocketError instead
        self._send_json_message({'error': error, 'details': details})

    def _send_json_message(self, json_object: dict) -> None:
        """Send a JSON object as message to the client."""
        text = dumps(json_object)
        logger.debug('Sending message to client %s: %s', self._client, text)
        self.sendMessage(text.encode())

    def onClose(self, was_clean: bool, code: int, reason: str):
        self.tracker.delete_all_subscriptions(self._client)
        clean_str = 'Clean' if was_clean else 'Unclean'
        logger.debug('%s close of WebSocket connection to %s; reason: %s',
                     clean_str, self._client, reason)


class EventDispatcher():

    """Dispatches events to interested clients."""

    # TODO define and implement required methods
