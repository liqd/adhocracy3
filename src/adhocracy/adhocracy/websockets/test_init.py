"""Tests for websockets package."""
import unittest

from substanced.util import get_oid

from adhocracy.websockets import ClientTracker


class DummyResource():

    """Dummy resource for testing."""

    def __init__(self, oid):
        """Initialize instance."""
        self.__oid__ = oid


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

    def test_duplicate_subscribe(self):
        """Test client subscribing same resource twice."""
        client = self._make_client()
        resource = self._make_resource()
        oid = get_oid(resource)
        result = self._tracker.subscribe(client, resource)
        assert result is True
        result = self._tracker.subscribe(client, resource)
        assert result is False
        assert len(self._tracker._clients2resource_oids) == 1
        assert len(self._tracker._resource_oids2clients) == 1
        assert self._tracker._clients2resource_oids[client] == {oid}
        assert self._tracker._resource_oids2clients[oid] == {client}

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

    def test_duplicate_unsubscribe(self):
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
