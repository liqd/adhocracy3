import unittest

from websocket import ABNF


class DummyClient():

    def __init__(self):
        self.messages_sent = False

    def send_messages(self):
        self.messages_sent = True


class DummyWSConnection():

    def __init__(self, dummy_frame: ABNF):
        self.dummy_frame = dummy_frame
        self.connected = True
        self.nothing_sent = True
        self.close_reason = None
        self.pong_text = None

    def recv_frame(self):
        return self.dummy_frame

    def send_close(self, reason: bytes):
        self.nothing_sent = False
        self.close_reason = reason

    def close(self):
        self.nothing_sent = False
        self.connected = False

    def pong(self, text):
        self.nothing_sent = False
        self.pong_text = text


class FunctionUnitTests(unittest.TestCase):

    def setUp(self):
        from pyramid.testing import DummyResource
        self._client = DummyClient()
        self._registry = DummyResource()
        self._registry.ws_client = self._client

    def test_send_messages_after_commit_hook_success(self):
        from adhocracy.websockets.client import send_messages_after_commit_hook
        send_messages_after_commit_hook(success=True, registry=self._registry)
        assert self._client.messages_sent is True

    def test_send_messages_after_commit_hook_no_success(self):
        from adhocracy.websockets.client import send_messages_after_commit_hook
        send_messages_after_commit_hook(success=False, registry=self._registry)
        assert self._client.messages_sent is False


class ClientUnitTests(unittest.TestCase):

    def _make_one(self, frame: ABNF):
        from adhocracy.websockets.client import Client
        client = Client(None)
        self._dummy_connection = DummyWSConnection(frame)
        client._ws_connection = self._dummy_connection
        return client

    def test_receive_text_frame(self):
        frame = ABNF(opcode=ABNF.OPCODE_TEXT, data='hello dear')
        client = self._make_one(frame)
        client._connect_and_receive_and_log_messages()
        assert self._dummy_connection.nothing_sent is True
        assert self._dummy_connection.connected is True

    def test_receive_close_frame(self):
        frame = ABNF(opcode=ABNF.OPCODE_CLOSE, data='time to say goodbye')
        client = self._make_one(frame)
        client._connect_and_receive_and_log_messages()
        assert self._dummy_connection.nothing_sent is False
        assert self._dummy_connection.connected is False
        assert self._dummy_connection.close_reason == b'server triggered close'

    def test_receive_ping_frame(self):
        frame = ABNF(opcode=ABNF.OPCODE_PING, data='hello')
        client = self._make_one(frame)
        client._connect_and_receive_and_log_messages()
        assert self._dummy_connection.nothing_sent is False
        assert self._dummy_connection.pong_text == 'Hi!'

    def test_receive_unexpected_frame(self):
        frame = ABNF(opcode=ABNF.OPCODE_BINARY, data='hello')
        client = self._make_one(frame)
        client._connect_and_receive_and_log_messages()
        assert self._dummy_connection.nothing_sent is True
        assert self._dummy_connection.connected is True

    def test_receive_none_frame(self):
        client = self._make_one(None)
        client._connect_and_receive_and_log_messages()
        assert self._dummy_connection.nothing_sent is True
        assert self._dummy_connection.connected is True


class TestFunctionalClient:

    # FIXME why didn't this work with a fixture instead of setUp/tearDown?
    def setUp(self):
        from adhocracy.websockets.client import Client
        self.client = Client(ws_url='ws://localhost:8080')

    def tearDown(self):
        self.client.stop()

    def test_create(self, websocket):
        try:
            self.setUp()
            assert self.client._is_running
            assert self.client._ws_connection.connected
        finally:
            self.tearDown()

    def test_stop(self, websocket):
        try:
            self.setUp()
            self.client.stop()
            assert not self.client._is_running
            assert not self.client._ws_connection.connected
        finally:
            self.tearDown()

    def test_send_messages(self, websocket):
        try:
            self.setUp()
            self.client._messages_to_send.add('dummy message')
            self.client._send_messages()
            assert 'dummy message' not in self.client._messages_to_send
        finally:
            self.tearDown()


class TestIntegrationClient:

    def test_includeme_without_ws_url_setting(self, dummy_config):
        from adhocracy.websockets.client import includeme
        dummy_config.registry.settings['adhocracy.ws_url'] = ''
        includeme(dummy_config)
        assert not hasattr(dummy_config.registry, 'ws_client')

    def test_includeme_with_ws_url_setting(self, websocket, dummy_config):
        from adhocracy.websockets.client import includeme
        from adhocracy.websockets.client import Client
        settings = dummy_config.registry.settings
        settings['adhocracy.ws_url'] = 'ws://localhost:8080'
        includeme(dummy_config)
        assert isinstance(dummy_config.registry.ws_client, Client)
