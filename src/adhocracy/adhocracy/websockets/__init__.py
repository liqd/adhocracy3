"""Asynchronous client-server communication via Websockets."""
from collections import defaultdict
from collections.abc import Iterable
from json import dumps
from json import loads
from logging import getLogger

from autobahn.asyncio.websocket import WebSocketServerProtocol
from autobahn.websocket.protocol import ConnectionRequest
from pyramid.traversal import resource_path
from substanced.util import get_oid
import colander

from adhocracy.websockets.schemas import ChildNotification
from adhocracy.websockets.schemas import ClientRequestSchema
from adhocracy.websockets.schemas import Notification
from adhocracy.websockets.schemas import StatusConfirmation
from adhocracy.websockets.schemas import VersionNotification
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IItemVersion


logger = getLogger(__name__)


class WebSocketError(Exception):

    """An error that occurs during communication with a WebSocket client."""

    def __init__(self, error_type: str, details: str):
        self.error_type = error_type
        self.details = details

    def __str__(self):
        return '{}: {}'.format(self.error_type, self.details)


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
    _tracker = ClientTracker()

    def __init__(self, context):
        """Create a new instance."""
        self._client_request_schema = self._bind_schema(ClientRequestSchema(),
                                                        context)
        self._status_confirmation = self._bind_schema(StatusConfirmation(),
                                                      context)
        self._notification = self._bind_schema(Notification(), context)
        self._child_notification = self._bind_schema(ChildNotification(),
                                                     context)
        self._version_notification = self._bind_schema(VersionNotification(),
                                                       context)

    def _bind_schema(self, schema: colander.MappingSchema,
                     context) -> colander.MappingSchema:
        return schema.bind(context=context)

    def onConnect(self, request: ConnectionRequest):  # noqa
        self._client = request.peer
        logger.debug('Client connecting: %s', self._client)

    def onOpen(self):  # noqa
        logger.debug('WebSocket connection to %s open', self._client)

    def onMessage(self, payload: bytes, is_binary: bool) -> None:    # noqa
        try:
            json_object = self._parse_message(payload, is_binary)
            request = self._convert_json_into_client_request(json_object)
            self._handle_client_request_and_send_response(request)
        except Exception as err:
            self._send_error_message(err)

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
            self._raise_if_unknown_field_value('action', err, json_object)
            self._raise_if_unknown_field_value('resource', err, json_object)
            self._raise_invalid_json_from_colander_invalid(err)
        except Exception as err:
            self._raise_invalid_json_from_exception(err)

    def _raise_if_unknown_field_value(
            self, field_name: str, err: colander.Invalid, json_object) -> None:
        """Raise an 'unknown_xxx' WebSocketError error if appropriate."""
        errdict = err.asdict()
        if self._is_only_key(errdict, field_name):
            field_value = self._return_value_from_dict_if_string(
                json_object, field_name)
            if field_value is not None:
                raise WebSocketError('unknown_' + field_name, field_value)

    def _is_only_key(self, d: dict, key: str) -> bool:
        return key in d and len(d) == 1

    def _return_value_from_dict_if_string(self, d: dict, key: str) -> str:
        if isinstance(d, dict) and key in d:
            value = d[key]
            if isinstance(value, str):
                return value

    def _raise_invalid_json_from_colander_invalid(self, err:
                                                  colander.Invalid) -> None:
        """Raise a 'invalid_json' WebSocketError from a colander error."""
        errdict = err.asdict()
        errlist = ['{}: {}'.format(k, errdict[k]) for k in errdict.keys()]
        details = ' / '.join(sorted(errlist))
        raise WebSocketError('invalid_json', details)

    def _raise_invalid_json_from_exception(self, err: Exception) -> None:
        """Raise a 'invalid_json' WebSocketError from a generic exception."""
        raise WebSocketError('invalid_json', str(err))

    def _handle_client_request_and_send_response(self, request: dict):
        action = request['action']
        resource = request['resource']
        self._raise_if_forbidden_request(action, resource)
        update_was_necessary = self._update_resource_subscription(action,
                                                                  resource)
        self._send_status_confirmation(update_was_necessary, action, resource)

    def _raise_if_forbidden_request(self, action: str,
                                    resource: IResource) -> None:
        """Raise an error if a client tries to subscribe to an ItemVersion."""
        if action == 'subscribe' and IItemVersion.providedBy(resource):
            raise WebSocketError('subscribe_not_supported',
                                 resource_path(resource))

    def _update_resource_subscription(self, action: str,
                                      resource: str) -> bool:
        """(Un)subscribe a client to/from a resource.

        :return: True if the request was necessary, False if it was an
                 unnecessary no-op
        """
        if action == 'subscribe':
            return self._tracker.subscribe(self._client, resource)
        else:
            return self._tracker.unsubscribe(self._client, resource)

    def _send_status_confirmation(self, update_was_necessary: bool,
                                  action: str, resource: IResource):
        status = 'ok' if update_was_necessary else 'redundant'
        json_message = self._status_confirmation.serialize(
            {'status': status, 'action': action, 'resource': resource})
        self._send_json_message(json_message)

    def _send_json_message(self, json_message: dict) -> None:
        """Send a JSON object as message to the client."""
        text = dumps(json_message)
        logger.debug('Sending message to client %s: %s', self._client, text)
        self.sendMessage(text.encode())

    def _send_error_message(self, err: Exception) -> None:
        if isinstance(err, WebSocketError):
            error = err.error_type
            details = err.details
        else:
            error = 'internal_error'
            details = str(err)
        self._send_json_message({'error': error, 'details': details})

    def send_modified_notification(self, resource: IResource) -> None:
        """Send notification about a modified resource."""
        self._send_json_message(self._notification.serialize(
            {'event': 'modified', 'resource': resource}))

    def send_child_notification(self, status: str, resource: IResource,
                                child: IResource) -> None:
        """Send notification concerning a child resource.

        :param status: should be 'new', 'removed', or 'modified'
        """
        self._send_json_message(self._child_notification.serialize(
            {'event': status + '_child',
             'resource': resource,
             'child': child}))

    def send_new_version_notification(self, resource: IResource,
                                      new_version: IResource) -> None:
        """Send notification if a new version has been added."""
        self._send_json_message(self._version_notification.serialize(
            {'event': 'new_version',
             'resource': resource,
             'version': new_version}))

    def onClose(self, was_clean: bool, code: int, reason: str):  # noqa
        self._tracker.delete_all_subscriptions(self._client)
        clean_str = 'Clean' if was_clean else 'Unclean'
        logger.debug('%s close of WebSocket connection to %s; reason: %s',
                     clean_str, self._client, reason)


class EventDispatcher():

    """Dispatches events to interested clients."""

    # TODO define and implement required methods
