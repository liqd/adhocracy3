"""Tests for websockets package."""
from substanced.util import get_oid
from . import ClientKeeper

import unittest


class DummyResource():

    """Dummy resource for testing."""

    def __init__(self, oid):
        """Initialize instance."""
        self.__oid__ = oid


class ClientKeeperUnitTests(unittest.TestCase):

    """Test the ClientKeeper class."""

    def _make_client(self):
        return object()

    def _make_resource(self):
        resource = DummyResource(self._next_oid)
        self._next_oid += 1
        return resource

    def setUp(self):
        """Test setup."""
        self._keeper = ClientKeeper()
        self._next_oid = 1

    def test_subscribe(self):
        """Test client subscription."""
        client = self._make_client()
        resource = self._make_resource()
        oid = get_oid(resource)
        self._keeper.subscribe(client, resource)
        assert len(self._keeper._clients2resource_oids) == 1
        assert len(self._keeper._resource_oids2clients) == 1
        assert self._keeper._clients2resource_oids[client] == {oid}
        assert self._keeper._resource_oids2clients[oid] == {client}

    def test_duplicate_subscribe(self):
        """Test client subscribing same resource twice."""
        client = self._make_client()
        resource = self._make_resource()
        oid = get_oid(resource)
        self._keeper.subscribe(client, resource)
        self._keeper.subscribe(client, resource)
        assert len(self._keeper._clients2resource_oids) == 1
        assert len(self._keeper._resource_oids2clients) == 1
        assert self._keeper._clients2resource_oids[client] == {oid}
        assert self._keeper._resource_oids2clients[oid] == {client}

    def test_subscribe_two_resources(self):
        """Test client subscribing to two resources."""
        client = self._make_client()
        resource1 = self._make_resource()
        resource2 = self._make_resource()
        oid1 = get_oid(resource1)
        oid2 = get_oid(resource2)
        self._keeper.subscribe(client, resource1)
        self._keeper.subscribe(client, resource2)
        assert len(self._keeper._clients2resource_oids) == 1
        assert len(self._keeper._resource_oids2clients) == 2
        assert self._keeper._clients2resource_oids[client] == {oid1, oid2}
        assert self._keeper._resource_oids2clients[oid1] == {client}
        assert self._keeper._resource_oids2clients[oid2] == {client}

    def test_subscribe_two_clients(self):
        """Test two clients subscribing to same resource."""
        client1 = self._make_client()
        client2 = self._make_client()
        resource = self._make_resource()
        oid = get_oid(resource)
        self._keeper.subscribe(client1, resource)
        self._keeper.subscribe(client2, resource)
        assert len(self._keeper._clients2resource_oids) == 2
        assert len(self._keeper._resource_oids2clients) == 1
        assert self._keeper._clients2resource_oids[client1] == {oid}
        assert self._keeper._clients2resource_oids[client2] == {oid}
        assert self._keeper._resource_oids2clients[oid] == {client1, client2}

    # TODO test:
    # def unsubscribe(self, client, resource):
    # test that double unsubscription has no effect
    # def delete_all_subscriptions(self, client):
    # delete client subscribed to 0/1/2 resource
    # def iterate_subscribers(self, resource):
    # test with 0/1/2 subscribers, also with subscriber for different resource
