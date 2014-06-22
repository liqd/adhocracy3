import pytest


class TestFunctionalClient:

    @pytest.fixture(scope='class')
    def websocket_client(self, request, websocket):
        from adhocracy.websockets.client import Client
        from adhocracy.websockets.client import URL
        client = Client.create(ws_url=URL)

        def tearDown():
            print('teardown websocket client')
            client._ws_connection.close()
        request.addfinalizer(tearDown)

        return client

    def test_create(self, websocket_client):
        inst = websocket_client
        assert inst.is_running
        assert inst._ws_connection.connected

    def test_stop(self, websocket_client):
        inst = websocket_client
        inst.stop()
        assert not inst.is_running
        assert not inst._ws_connection.connected

    def test__send_messages(self, websocket_client):
        inst = websocket_client
        inst._messages_to_send.add('dummy message')
        inst._send_messages()
        assert 'dummy message' not in inst._messages_to_send


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


