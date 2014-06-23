from json import dumps
from json import loads
import unittest
import pytest

from pyramid import testing
from substanced.util import get_oid
from zope.interface import alsoProvides

from adhocracy.interfaces import IItemVersion
from adhocracy.websockets import ClientCommunicator
from adhocracy.websockets import ClientTracker
from adhocracy.websockets import WebSocketError
# REVIEW code to test should be import in the unit test


class DummyResource():

    """Dummy resource for testing."""

    def __init__(self, oid):
        """Initialize instance."""
        self.__oid__ = oid


class DummyConnectionRequest():

    def __init__(self, peer: str):
        self.peer = peer


class DummyZODBConnection():

    def __init__(self, zodb_root=None):
        self.zodb_root = zodb_root

    def sync(self):
        pass

    def root(self):
        return self.zodb_root or {}


class QueueingClientCommunicator(ClientCommunicator):

    """ClientCommunicator that adds outgoing messages to an internal queue."""

    def __init__(self):
        super().__init__()
        self.queue = []

    def sendMessage(self, payload: bytes):
        """Decode message back into JSON object and add it to the queue."""
        json_message = loads(payload.decode())
        self.queue.append(json_message)


class WebSocketErrorUnitTests(unittest.TestCase):

    """Test the WebSocketError class."""

    def test_str(self):
        err = WebSocketError('malformed_message', 'message is binary')
        assert str(err) == 'malformed_message: message is binary'


class ClientCommunicatorUnitTests(unittest.TestCase):

    """Test the ClientCommunicator class."""

    def setUp(self):
        """Test setup."""
        self._next_oid = 1
        self._child = self._make_resource()
        app_root = self._make_resource()
        app_root['child'] = self._child
        zodb_root = self._make_resource()
        zodb_root['app_root'] = app_root
        app_root.__parent__ = None
        app_root.__name__ = None
        QueueingClientCommunicator.zodb_connection = DummyZODBConnection(
            zodb_root=zodb_root)
        self._comm = QueueingClientCommunicator()
        self._peer = "websocket peer"
        self._connect()

    def tearDown(self):
        self._comm.onClose(True, 0, 'teardown')

    def _make_resource(self, *args):
        resource = testing.DummyResource(*args)
        resource.__oid__ = self._next_oid
        self._next_oid += 1
        return resource

    def test_autobahn_installed(self):
        """Test that Autobahn is installed."""
        from autobahn import __version__
        assert isinstance(__version__, str)

    def test_onConnect(self):
        self._connect()
        assert self._comm._client == self._peer
        assert len(self._comm.queue) == 0

    def _connect(self, peer=None):
        if peer == None:
            peer = self._peer
        request = DummyConnectionRequest(peer)
        self._comm.onConnect(request)

    def test_onOpen(self):
        self._comm.onOpen()
        assert len(self._comm.queue) == 0

    def test_onMessage_valid_subscribe(self):
        msg = self._build_message({'action': 'subscribe',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'status': 'ok',
                                       'action': 'subscribe',
                                       'resource': '/child'}

    def _build_message(self, json_message: dict) -> bytes:
        return dumps(json_message).encode()

    def test_onMessage_valid_unsubscribe(self):
        msg = self._build_message({'action': 'subscribe',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        msg = self._build_message({'action': 'unsubscribe',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 2
        assert self._comm.queue[-1] == {'status': 'ok',
                                        'action': 'unsubscribe',
                                        'resource': '/child'}

    def test_onMessage_redundant_subscribe(self):
        msg = self._build_message({'action': 'subscribe',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 2
        assert self._comm.queue[-1] == {'status': 'redundant',
                                        'action': 'subscribe',
                                        'resource': '/child'}

    def test_onMessage_resubscribe_after_unsubscribe(self):
        msg = self._build_message({'action': 'subscribe',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        msg = self._build_message({'action': 'unsubscribe',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        msg = self._build_message({'action': 'subscribe',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 3
        assert self._comm.queue[-1] == {'status': 'ok',
                                        'action': 'subscribe',
                                        'resource': '/child'}

    def test_onMessage_subscribe_item_version(self):
        alsoProvides(self._child, IItemVersion)
        msg = self._build_message({'action': 'subscribe',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'error': 'subscribe_not_supported',
                                       'details': '/child'}

    def test_onMessage_with_binary_message(self):
        self._comm.onMessage(b'DEADBEEF', True)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'error': 'malformed_message',
                                       'details': 'message is binary'}

    def test_onMessage_with_invalid_json(self):
        self._comm.onMessage('This is not a JSON dict'.encode(), False)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'error': 'malformed_message',
           'details': 'No JSON object could be decoded'}

    def test_onMessage_with_json_array(self):
        msg = self._build_message(['This', 'is an array', 'not a dict'])
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 1
        last_message = self._comm.queue[0]
        assert last_message['error'] == 'invalid_json'
        assert 'not a mapping type' in last_message['details']

    def test_onMessage_with_wrong_field(self):
        msg = self._build_message({'event': 'created',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'error': 'invalid_json',
                                       'details': 'action: Required'}

    def test_onMessage_with_invalid_action(self):
        msg = self._build_message({'action': 'just do it!',
                                   'resource': '/child'})
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'error': 'unknown_action',
                                       'details': 'just do it!'}

    def test_onMessage_with_invalid_resource(self):
        msg = self._build_message({'action': 'subscribe',
                                   'resource': '/wrong_child'})
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'error': 'unknown_resource',
                                       'details': '/wrong_child'}

    def test_onMessage_with_both_invalid(self):
        msg = self._build_message({'action': 'just do it!',
                                   'resource': '/wrong_child'})
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 1
        last_message = self._comm.queue[0]
        assert last_message['error'] == 'invalid_json'
        assert 'action' in last_message['details']
        assert 'resource' in last_message['details']

    def test_onMessage_with_invalid_json_type(self):
        msg = self._build_message({'action': 'subscribe',
                                   'resource': 7})
        self._comm.onMessage(msg, False)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'error': 'invalid_json',
            'details': 'coercing to str: need bytes, bytearray or '
                       'buffer-like object, int found'}

    def test_send_modified_notification(self):
        self._comm.send_modified_notification(self._child)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'event': 'modified',
                                       'resource': '/child'}

    def test_send_child_notification(self):
        grandchild = self._make_resource('grandchild', self._child)
        self._comm.send_child_notification('new', self._child, grandchild)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'event': 'new_child',
                                       'resource': '/child',
                                       'child': '/child/grandchild'}

    def test_send_new_version_notification(self):
        new_version = self._make_resource('version_007', self._child)
        self._comm.send_new_version_notification(self._child, new_version)
        assert len(self._comm.queue) == 1
        assert self._comm.queue[0] == {'event': 'new_version',
                                       'resource': '/child',
                                       'version': '/child/version_007'}

    def test_client_may_send_notifications_if_localhost(self):
        self._connect('localhost:1234')
        assert self._comm._client_may_send_notifications is True

    def test_client_may_send_notifications_if_localhost_ipv4(self):
        self._connect('127.0.0.1:1234')
        assert self._comm._client_may_send_notifications is True

    def test_client_may_not_send_notifications_if_not_localhost(self):
        self._connect('78.46.75.118:1234')
        assert self._comm._client_may_send_notifications is False


class ClientTrackerUnitTests(unittest.TestCase):

    """Test the ClientTracker class."""

    def _make_client(self):
        return object()

    def _make_resource(self):
        resource = DummyResource(self._next_oid)
        self._next_oid += 1
        return resource

    def setUp(self):
        """Test setup."""
        self._tracker = ClientTracker()
        self._next_oid = 1

    def test_subscribe(self):
        """Test client subscription."""
        client = self._make_client()
        resource = self._make_resource()
        oid = get_oid(resource)
        result = self._tracker.subscribe(client, resource)
        assert result is True
        assert len(self._tracker._clients2resource_oids) == 1
        assert len(self._tracker._resource_oids2clients) == 1
        assert self._tracker._clients2resource_oids[client] == {oid}
        assert self._tracker._resource_oids2clients[oid] == {client}

    def test_redundant_subscribe(self):
        """Test client subscribing same resource twice."""
        # REVIEW:
        # The docstring is redundant, the method name shows the same
        # information and docstrings are not need for tests anyway.
        # The method name should start with 'subscribe' like the other tests
        # testing the same method and clean code naming.
        client = self._make_client()
        resource = self._make_resource()
        oid = get_oid(resource)
        result = self._tracker.subscribe(client, resource)
        # REVIEW: The following assert is not what we want to test here.
        assert result is True
        # REVIEW: Actually this is what we are testing
        result = self._tracker.subscribe(client, resource)
        assert result is False
        # REVIEW: The following asserts are also redundant (its already testet above)
        assert len(self._tracker._clients2resource_oids) == 1
        assert len(self._tracker._resource_oids2clients) == 1
        assert self._tracker._clients2resource_oids[client] == {oid}
        assert self._tracker._resource_oids2clients[oid] == {client}

        # REVIEW [joka]:
        # Unit tests should follow the 'if when then' pattern
        # and test one 'thing' only (ideally only one assert).
        # This is part of the  unit test concept and our clean code guideline.
        # It makes refactoring and reading much faster.

        # I don't say we have to rewrite the tests beforge merge. I just want
        # that we have a common understanding when we refactore or extend
        # these tests.

    def test_subscribe_two_resources(self):
        """Test client subscribing to two resources."""
        client = self._make_client()
        resource1 = self._make_resource()
        resource2 = self._make_resource()
        oid1 = get_oid(resource1)
        oid2 = get_oid(resource2)
        result1 = self._tracker.subscribe(client, resource1)
        result2 = self._tracker.subscribe(client, resource2)
        assert result1 is True
        assert result2 is True
        assert len(self._tracker._clients2resource_oids) == 1
        assert len(self._tracker._resource_oids2clients) == 2
        assert self._tracker._clients2resource_oids[client] == {oid1, oid2}
        assert self._tracker._resource_oids2clients[oid1] == {client}
        assert self._tracker._resource_oids2clients[oid2] == {client}

    def test_subscribe_two_clients(self):
        """Test two clients subscribing to same resource."""
        client1 = self._make_client()
        client2 = self._make_client()
        resource = self._make_resource()
        oid = get_oid(resource)
        result1 = self._tracker.subscribe(client1, resource)
        result2 = self._tracker.subscribe(client2, resource)
        assert result1 is True
        assert result2 is True
        assert len(self._tracker._clients2resource_oids) == 2
        assert len(self._tracker._resource_oids2clients) == 1
        assert self._tracker._clients2resource_oids[client1] == {oid}
        assert self._tracker._clients2resource_oids[client2] == {oid}
        assert self._tracker._resource_oids2clients[oid] == {client1, client2}

    def test_unsubscribe(self):
        """Test client unsubscription."""
        client = self._make_client()
        resource = self._make_resource()
        self._tracker.subscribe(client, resource)
        result = self._tracker.unsubscribe(client, resource)
        assert result is True
        assert len(self._tracker._clients2resource_oids) == 0
        assert len(self._tracker._resource_oids2clients) == 0

    def test_redundant_unsubscribe(self):
        """Test client unsubscribing from the same resource twice."""
        client = self._make_client()
        resource = self._make_resource()
        self._tracker.subscribe(client, resource)
        result = self._tracker.unsubscribe(client, resource)
        assert result is True
        assert len(self._tracker._clients2resource_oids) == 0
        assert len(self._tracker._resource_oids2clients) == 0
        result = self._tracker.unsubscribe(client, resource)
        assert result is False
        assert len(self._tracker._clients2resource_oids) == 0
        assert len(self._tracker._resource_oids2clients) == 0

    def test_delete_all_subscriptions_empty(self):
        """Test deleting all subscriptions for a client that has none."""
        client = self._make_client()
        self._tracker.delete_all_subscriptions(client)
        assert len(self._tracker._clients2resource_oids) == 0
        assert len(self._tracker._resource_oids2clients) == 0

    def test_delete_all_subscriptions_two_resource(self):
        """Test deleting all subscriptions for a client that has two."""
        client = self._make_client()
        resource1 = self._make_resource()
        resource2 = self._make_resource()
        self._tracker.subscribe(client, resource1)
        self._tracker.subscribe(client, resource2)
        self._tracker.delete_all_subscriptions(client)
        assert len(self._tracker._clients2resource_oids) == 0
        assert len(self._tracker._resource_oids2clients) == 0

    def test_delete_all_subscriptions_two_clients(self):
        """Test deleting all subscriptions for one client subscribed to the
        same resource as another one.

        """

        client1 = self._make_client()
        client2 = self._make_client()
        resource = self._make_resource()
        oid = get_oid(resource)
        self._tracker.subscribe(client1, resource)
        self._tracker.subscribe(client2, resource)
        self._tracker.delete_all_subscriptions(client1)
        assert len(self._tracker._clients2resource_oids) == 1
        assert len(self._tracker._resource_oids2clients) == 1
        assert self._tracker._clients2resource_oids[client2] == {oid}
        assert self._tracker._resource_oids2clients[oid] == {client2}
        assert client1 not in self._tracker._clients2resource_oids

    def test_iterate_subscribers_empty(self):
        """Test iterating subscribers for a resource that has none."""
        resource = self._make_resource()
        result = list(self._tracker.iterate_subscribers(resource))
        assert len(result) == 0
        assert len(self._tracker._clients2resource_oids) == 0
        assert len(self._tracker._resource_oids2clients) == 0

    def test_iterate_subscribers_two(self):
        """Test iterating subscribers for a resource that has two."""
        client1 = self._make_client()
        client2 = self._make_client()
        resource = self._make_resource()
        self._tracker.subscribe(client1, resource)
        self._tracker.subscribe(client2, resource)
        result = list(self._tracker.iterate_subscribers(resource))
        assert len(result) == 2
        assert client1 in result
        assert client2 in result


class TestFunctionalClientCommunicator:

    @pytest.fixture(scope='function')
    def websocket_connection(self, request, server):
        from websocket import create_connection
        connection = create_connection("ws://localhost:8080")
        connection.send('{"resource": "/adhocracy", "action": "subscribe"}')
        connection.recv()

        def tearDown():
            print('teardown websocket connection')
            connection.close()
        request.addfinalizer(tearDown)

        return connection

    def _add_pool(self, server, path, name):
        import json
        import requests
        from adhocracy.resources.pool import IBasicPool
        url = server.application_url + 'adhocracy' + path
        data = {'content_type': IBasicPool.__identifier__,
                'data': {'adhocracy.sheets.name.IName': {'name': name}}}
        requests.post(url, data=json.dumps(data),
                      headers = {'content-type': 'application/json'})

    def test_send_child_notification(self, server, websocket_connection):
        self._add_pool(server, '/', 'Proposals')
        assert 'Proposals' in websocket_connection.recv()

