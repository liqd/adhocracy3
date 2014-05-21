"""Asynchronous client-server communication via Websockets."""
from collections import defaultdict
from collections.abc import Iterable
from logging import getLogger

from autobahn.asyncio.websocket import WebSocketServerProtocol
from substanced.util import get_oid

from adhocracy.interfaces import IResource


logger = getLogger(__name__)


class ClientCommunicator(WebSocketServerProtocol):

    """Communicates with a client through a Websocket connection."""

    def onConnect(self, request):
        # TODO reqister myself
        self._client = request.peer
        logger.debug('Client connecting: %s', self._client)

    def onOpen(self):
        logger.debug('WebSocket connection to %s open', self._client)

    def onMessage(self, payload, is_binary):
        if is_binary:
            print('Binary message received: {0} bytes'.format(len(payload)))
        else:
            print('Text message received: {0}'.format(payload.decode('utf8')))

        # TODO handle message and send suitable response
        self.sendMessage(payload, is_binary)

    def onClose(self, was_clean, code, reason):
        # TODO delete all subscriptions
        print('WebSocket connection closed: {0}'.format(reason))


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


class EventDispatcher():

    """Dispatches events to interested clients."""

    # TODO define and implement required methods
