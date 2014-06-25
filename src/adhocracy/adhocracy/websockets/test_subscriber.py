import unittest

from pyramid.testing import DummyResource
from pyramid.threadlocal import get_current_registry


class DummyClient():

    def __init__(self):
        self.resource_created = False
        self.resource_modified = False

    def add_message_resource_created(self, resource):
        self.resource_created = True

    def add_message_resource_modified(self, resource):
        self.resource_modified = True


class FunctionUnitTests(unittest.TestCase):

    """Test the functions defined by the subscriber module."""

    def setUp(self):
        self._event = DummyResource()
        self._event.object = DummyResource()
        self._registry = get_current_registry()
        self._old_ws_client = getattr(self._registry, 'ws_client', None)

    def tearDown(self):
        setattr(self._registry, 'ws_client', self._old_ws_client)

    def test_resource_created_and_added_subscriber(self):
        from adhocracy.websockets.subscriber import \
            resource_created_and_added_subscriber
        client = DummyClient()
        self._registry.ws_client = client
        resource_created_and_added_subscriber(self._event)
        assert client.resource_created is True

    def test_resource_modified_subscriber(self):
        from adhocracy.websockets.subscriber import \
            resource_modified_subscriber
        client = DummyClient()
        self._registry.ws_client = client
        resource_modified_subscriber(self._event)
        assert client.resource_modified is True

    def test_resource_created_and_added_subscriber_no_client(
            self):
        """Call should pass without exceptions if there is no client."""
        from adhocracy.websockets.subscriber import \
            resource_created_and_added_subscriber
        del self._registry.ws_client
        resource_created_and_added_subscriber(self._event)

    def test_resource_modified_subscriber_no_client(self):
        """Call should pass without exceptions if there is no client."""
        from adhocracy.websockets.subscriber import \
            resource_modified_subscriber
        del self._registry.ws_client
        resource_modified_subscriber(self._event)
