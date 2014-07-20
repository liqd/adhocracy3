import unittest

from pyramid import testing


class ConfigViewTest(unittest.TestCase):

    def _callFUT(self, request):
        from adhocracy.frontend import config_view
        return config_view(request)

    def test_with_empty_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = None
        assert self._callFUT(request) == \
            {'ws_url': 'ws://example.com:80',
             'template_path': '/frontend_static/templates',
             'root_path': '/adhocracy',
             }

    def test_ws_url_with_ws_url_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.frontend.ws_url': 'ws://l.x'}
        assert self._callFUT(request)['ws_url'] == 'ws://l.x'

    def test_ws_url_with_adhocracy_ws_url_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.ws_url': 'ws://localhost:8888'}
        assert self._callFUT(request)['ws_url'] == 'ws://example.com:8888'

    def test_ws_url_with_port_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.ws_url': 'ws://localhost:8888'}
        assert self._callFUT(request)['ws_url'] == 'ws://example.com:8888'

    def test_template_path_with_template_path_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.frontend.template_path': '/t'}
        assert self._callFUT(request)['template_path'] == '/t'

    def test_root_path_with_platform_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.platform_id': 'adhocracy2'}
        assert self._callFUT(request)['root_path'] == '/adhocracy2'


class ViewsFunctionalTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.frontend import main
        from webtest import TestApp
        app = main({})
        self.testapp = TestApp(app)

    def test_static_view(self):
        resp = self.testapp.get('/frontend_static/root.html', status=200)
        assert '200' in resp.status

    def test_config_json_view(self):
        resp = self.testapp.get('/frontend_config.json', status=200)
        assert '200' in resp.status

