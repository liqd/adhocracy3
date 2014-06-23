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
            assert self.client.is_running
            assert self.client._ws_connection.connected
        finally:
            self.tearDown()

    def test_stop(self, websocket):
        try:
            self.setUp()
            self.client.stop()
            assert not self.client.is_running
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
        dummy_config.registry.settings['adhocracy.ws_url'] = 'ws://localhost:8080'
        includeme(dummy_config)
        assert isinstance(dummy_config.registry.ws_client, Client)
