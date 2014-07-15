import unittest

from pyramid import testing


class DummyClient():

    def __init__(self):
        self.resource_created = False
        self.resource_modified = False

    def add_message_resource_created(self, resource):
        self.resource_created = True

    def add_message_resource_modified(self, resource):
        self.resource_modified = True


def _create_dummy_event_with_client(ws_client):
    registry = testing.DummyResource(ws_client=ws_client)
    event = testing.DummyResource(registry=registry,
                          object=None)
    return event


class ResourceCreatedAndAddedSubscriberUnitTests(unittest.TestCase):

    def _call_fut(self, event):
        from adhocracy.websockets.subscriber import \
            resource_created_and_added_subscriber
        return resource_created_and_added_subscriber(event)

    def test_with_client(self):
        client = DummyClient()
        event = _create_dummy_event_with_client(client)
        self._call_fut(event)
        assert client.resource_created is True

    def test_with_none_client(self):
        event = _create_dummy_event_with_client(None)
        assert self._call_fut(event) is None

    def test_without_client(self):
        event = _create_dummy_event_with_client(None)
        delattr(event.registry, 'ws_client')
        assert self._call_fut(event) is None

    def test_with_none_registry(self):
        event = _create_dummy_event_with_client(None)
        event.registry = None
        assert self._call_fut(event) is None


class ResourceModifiedSubscriberUnitTests(unittest.TestCase):

    def _call_fut(self, event):
        from adhocracy.websockets.subscriber import \
            resource_modified_subscriber
        return resource_modified_subscriber(event)

    def test_with_client(self):
        client = DummyClient()
        event = _create_dummy_event_with_client(client)
        self._call_fut(event)
        assert client.resource_modified is True

    def test_with_none_client(self):
        event = _create_dummy_event_with_client(None)
        assert self._call_fut(event) is None

    def test_without_client(self):
        event = _create_dummy_event_with_client(None)
        delattr(event.registry, 'ws_client')
        assert self._call_fut(event) is None

    def test_with_none_registry(self):
        event = _create_dummy_event_with_client(None)
        event.registry = None
        assert self._call_fut(event) is None


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.websockets.subscriber')
        self.handlers = [x.handler.__name__ for x
                         in self.config.registry.registeredHandlers()]

    def tearDown(self):
        testing.tearDown()

    def test_register_created_subscriber(self):
        from adhocracy.websockets.subscriber import resource_created_and_added_subscriber
        assert resource_created_and_added_subscriber.__name__ in self.handlers

    def test_register_modified_subscriber(self):
        from adhocracy.websockets.subscriber import resource_modified_subscriber
        assert resource_modified_subscriber.__name__ in self.handlers
