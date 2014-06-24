"""Classes used by the standalone Websocket server."""
from collections import defaultdict
from collections import Hashable
from collections import Iterable
from json import dumps
from json import loads
import logging

from autobahn.asyncio.websocket import WebSocketServerProtocol
from autobahn.websocket.protocol import ConnectionRequest
from pyramid.traversal import resource_path
from substanced.util import get_oid
import colander

from adhocracy.interfaces import IResource
from adhocracy.interfaces import IItemVersion
from adhocracy.websockets import WebSocketError
from adhocracy.websockets.schemas import ClientRequestSchema
from adhocracy.websockets.schemas import Notification
from adhocracy.websockets.schemas import StatusConfirmation
from adhocracy.websockets.schemas import ChildNotification
from adhocracy.websockets.schemas import VersionNotification


logger = logging.getLogger(__name__)


class ClientTracker():

    """"Keeps track of the clients that want notifications."""

    def __init__(self):
        self._clients2resource_oids = defaultdict(set)
        self._resource_oids2clients = defaultdict(set)

    def is_subscribed(self, client: Hashable, resource: IResource) -> bool:
        """Check whether a client is subscribed to a resource."""
        oid = get_oid(resource)
        return (client in self._clients2resource_oids and
                oid in self._clients2resource_oids[client])

    def subscribe(self, client: Hashable, resource: IResource) -> bool:
        """Subscribe a client to a resource, if necessary.

        :return: True if the subscription was successful, False if it was
                 unnecessary (the client was already subscribed).
        """
        if self.is_subscribed(client, resource):
            return False
        oid = get_oid(resource)
        self._clients2resource_oids[client].add(oid)
        self._resource_oids2clients[oid].add(client)
        return True

    def unsubscribe(self, client: Hashable, resource: IResource) -> bool:
        """Unsubscribe a client from a resource, if necessary.

        :return: True if the unsubscription was successful, False if it was
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
        # REVIEW: the name 'mulitidict' in the method name and parameter is
        # misleading. Multidicts are dicts with non unique keys, instead we
        # expect a dict with set values.
        multidict[key].discard(value)
        if not multidict[key]:
            del multidict[key]

    def delete_all_subscriptions(self, client: Hashable) -> None:
        """Delete all subscriptions for a client."""
        # REVIEW [joka]: Annotating the return value None is not a usefull
        # information because all callables have None as default return value.
        # In addition if we start doing this here we also have to do it for all
        # other callables and this means  work.
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

    """Communicates with a client through a WebSocket connection.

    Note that the `zodb_connection` attribute **must** be set
    instances of this class can be used!
    """

    # All instances of this class share the same zodb connection object
    zodb_connection = None
    # All instances of this class share the same tracker
    _tracker = ClientTracker()

    def get_context(self):
        """Get a context object to resolve resource paths.

        :raises KeyError: if the zodb root has no app_root child.
        :raises AttributeError: if the `zodb_connection` attribute is None.

        """
        self.zodb_connection.sync()
        root = self.zodb_connection.root()
        return root['app_root']

    def onConnect(self, request: ConnectionRequest):  # noqa
        self._client = request.peer
        self._client_may_send_notifications = self._client_runs_on_localhost()
        logger.debug('Client connecting: %s', self._client)

    def _client_runs_on_localhost(self):
        return any(self._client.startswith(prefix) for prefix in
                   ('localhost:', '127.0.0.1:', '::1:'))

    def onOpen(self):  # noqa
        logger.debug('WebSocket connection to %s open', self._client)

    def onMessage(self, payload: bytes, is_binary: bool) -> None:    # noqa
        try:
            json_object = self._parse_message(payload, is_binary)
            if self._handle_if_event_notification(json_object):
                return
            context = self.get_context()
            request = self._parse_json_via_schema(json_object,
                                                  ClientRequestSchema,
                                                  context)
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

    def _handle_if_event_notification(self, json_object) -> bool:
        """Handle message if it's a notifications from our Pyramid app.

        :return: True if the message is a valid event notification from our
                 Pyramid app and has been handled; False otherwise
        """
        if (self._client_may_send_notifications and
                self._looks_like_event_notification(json_object)):
            context = self.get_context()
            notification = self._parse_json_via_schema(json_object,
                                                       Notification,
                                                       context,)
            self._dispatch_event_notification_to_subscribers(notification)
            return True
        else:
            return False

    def _parse_json_via_schema(self, json_object, schema:
                               colander.MappingSchema, context) -> dict:
        try:
            schema_with_context = schema().bind(context=context)
            return schema_with_context.deserialize(json_object)
        except colander.Invalid as err:
            self._raise_if_unknown_field_value('action', err, json_object)
            self._raise_if_unknown_field_value('resource', err, json_object)
            self._raise_invalid_json_from_colander_invalid(err)
        except Exception as err:
            self._raise_invalid_json_from_exception(err)

    def _handle_client_request_and_send_response(self, request: dict) -> None:
        action = request['action']
        resource = request['resource']
        self._raise_if_forbidden_request(action, resource)
        update_was_necessary = self._update_resource_subscription(action,
                                                                  resource)
        self._send_status_confirmation(update_was_necessary, action, resource)

    def _send_error_message(self, err: Exception) -> None:
        if isinstance(err, WebSocketError):
            error = err.error_type
            details = err.details
        else:  # pragma: no cover
            logger.exception(
                'Unexpected error while handling Websocket request')
            error = 'internal_error'
            details = '{}: {}'.format(err.__class__.__name__, err)
        self._send_json_message({'error': error, 'details': details})

    def _looks_like_event_notification(self, json_object) -> bool:
        return isinstance(json_object, dict) and 'event' in json_object

    def _dispatch_event_notification_to_subscribers(self, notification:
                                                    dict) -> None:
        event = notification['event']
        resource = notification['resource']
        if event == 'created':
            self._dispatch_created_event(resource)
        elif event == 'modified':
            self._dispatch_modified_event(resource)
        elif event == 'deleted':
            self._dispatch_deleted_event(resource)
        else:
            details = 'unknown event: {}'.format(event)
            raise WebSocketError('invalid_json', details)

    def _raise_if_unknown_field_value(self, field_name: str,
                                      err: colander.Invalid,
                                      json_object: dict) -> None:
        """Raise an 'unknown_xxx' WebSocketError error if appropriate."""
        errdict = err.asdict()
        if (self._is_only_key(errdict, field_name) and
                field_name in json_object):
            field_value = json_object[field_name]
            raise WebSocketError('unknown_' + field_name, field_value)

    def _is_only_key(self, d: dict, key: str) -> bool:
        return key in d and len(d) == 1

    def _raise_invalid_json_from_colander_invalid(self, err:
                                                  colander.Invalid) -> None:
        """Raise a 'invalid_json' WebSocketError from a colander error."""
        errdict = err.asdict()
        errlist = ['{}: {}'.format(k, errdict[k]) for k in errdict.keys()]
        details = ' / '.join(sorted(errlist))
        raise WebSocketError('invalid_json', details)
    # REVIEW: the docstring is not necessary, the method name gives you the
    # same information.

    def _raise_invalid_json_from_exception(self, err: Exception) -> None:
        """Raise a 'invalid_json' WebSocketError from a generic exception."""
        raise WebSocketError('invalid_json', str(err))

    def _raise_if_forbidden_request(self, action: str,
                                    resource: IResource) -> None:
        """Raise an error if a client tries to subscribe to an ItemVersion."""
        if action == 'subscribe' and IItemVersion.providedBy(resource):
            raise WebSocketError('subscribe_not_supported',
                                 resource_path(resource))

    def _update_resource_subscription(self, action: str,
                                      resource: str) -> bool:
        """(Un)subscribe this instance to/from a resource.

        :return: True if the request was necessary, False if it was an
                 unnecessary no-op
        """
        if action == 'subscribe':
            return self._tracker.subscribe(self, resource)
        else:
            return self._tracker.unsubscribe(self, resource)

    def _send_status_confirmation(self, update_was_necessary: bool,
                                  action: str, resource: IResource):
        status = 'ok' if update_was_necessary else 'redundant'
        context = self.get_context()
        schema = StatusConfirmation().bind(context=context)
        json_message = schema.serialize(
            {'status': status, 'action': action, 'resource': resource})
        self._send_json_message(json_message)

    def _send_json_message(self, json_message: dict) -> None:
        """Send a JSON object as message to the client."""
        text = dumps(json_message)
        logger.debug('Sending message to client %s: %s', self._client, text)
        self.sendMessage(text.encode())

    def _dispatch_created_event(self, resource: IResource) -> None:
        parent = self._get_parent(resource)
        if parent is not None:
            if IItemVersion.providedBy(resource):
                self._notify_new_version(parent, resource)
            else:
                self._notify_new_child(parent, resource)

    def _dispatch_modified_event(self, resource: IResource) -> None:
        self._notify_resource_modified(resource)
        parent = self._get_parent(resource)
        if parent is not None:
            self._notify_modified_child(parent, resource)

    def _dispatch_deleted_event(self, resource: IResource) -> None:
        # FIXME Should we also notify subscribers of the deleted resource?
        # That's currently not part of the API.
        parent = self._get_parent(resource)
        if parent is not None:
            self._notify_removed_child(parent, resource)

    def _get_parent(self, resource: IResource) -> IResource:
        """Return the parent of a resource.

        If no parent exists, None is returned and a warning is logged.
        """
        parent = getattr(resource, '__parent__', None)
        if parent is None:
            logger.warning('Resource has no parent: %s',
                           resource_path(resource))
        return parent

    def _notify_new_version(self, parent: IResource,
                            new_version: IItemVersion) -> None:
        """Notify subscribers if a new version has been added to an item."""
        for client in self._tracker.iterate_subscribers(parent):
            client.send_new_version_notification(parent, new_version)

    def _notify_new_child(self, parent: IResource, child: IResource) -> None:
        """Notify subscribers if a child has been added to a pool or item."""
        for client in self._tracker.iterate_subscribers(parent):
            client.send_child_notification('new', parent, child)

    def _notify_resource_modified(self, resource: IResource) -> None:
        """Notify subscribers if a resource has been modified."""
        for client in self._tracker.iterate_subscribers(resource):
            client.send_modified_notification(resource)

    def _notify_modified_child(self, parent: IResource,
                               child: IResource) -> None:
        """Notify subscribers if a child in a pool has been modified."""
        for client in self._tracker.iterate_subscribers(parent):
            client.send_child_notification('modified', parent, child)

    def _notify_removed_child(self, parent: IResource,
                              child: IResource) -> None:
        """Notify subscribers if a child has been removed from a pool."""
        for client in self._tracker.iterate_subscribers(parent):
            client.send_child_notification('removed', parent, child)

    def send_modified_notification(self, resource: IResource) -> None:
        """Send notification about a modified resource."""
        context = self.get_context()
        schema = Notification().bind(context=context)
        data = schema.serialize({'event': 'modified', 'resource': resource})
        self._send_json_message(data)

    def send_child_notification(self, status: str, resource: IResource,
                                child: IResource) -> None:
        """Send notification concerning a child resource.

        :param status: should be 'new', 'removed', or 'modified'
        """
        context = self.get_context()
        schema = ChildNotification().bind(context=context)
        data = schema.serialize({'event': status + '_child',
                                 'resource': resource,
                                 'child': child})
        self._send_json_message(data)

    def send_new_version_notification(self, resource: IResource,
                                      new_version: IResource) -> None:
        """Send notification if a new version has been added."""
        context = self.get_context()
        schema = VersionNotification().bind(context=context)
        data = schema.serialize({'event': 'new_version',
                                 'resource': resource,
                                 'version': new_version})
        self._send_json_message(data)

    def onClose(self, was_clean: bool, code: int, reason: str):  # noqa
        self._tracker.delete_all_subscriptions(self)
        clean_str = 'Clean' if was_clean else 'Unclean'
        logger.debug('%s close of WebSocket connection to %s; reason: %s',
                     clean_str, self._client, reason)
