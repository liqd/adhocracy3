import unittest

from pyramid import testing


class ConfigViewTest(unittest.TestCase):

    def _call_fut(self, request):
        from adhocracy.frontend import config_view
        return config_view(request)

    def test_with_empty_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = None
        assert self._call_fut(request) == \
            {'ws_url': 'ws://example.com:80',
             'pkg_path': '/static/js/Packages',
             'root_path': '/adhocracy',
             }

    def test_ws_url_with_ws_url_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.frontend.ws_url': 'ws://l.x'}
        assert self._call_fut(request)['ws_url'] == 'ws://l.x'

    def test_ws_url_with_adhocracy_ws_url_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.ws_url': 'ws://localhost:8888'}
        assert self._call_fut(request)['ws_url'] == 'ws://example.com:8888'

    def test_ws_url_with_port_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.ws_url': 'ws://localhost:8888'}
        assert self._call_fut(request)['ws_url'] == 'ws://example.com:8888'

    def test_pkg_path_with_pkg_path_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.frontend.pkg_path': '/t'}
        assert self._call_fut(request)['pkg_path'] == '/t'

    def test_root_path_with_platform_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {'adhocracy.platform_id': 'adhocracy2'}
        assert self._call_fut(request)['root_path'] == '/adhocracy2'


class RootViewTest(unittest.TestCase):

    def _call_fut(self, request):
        from adhocracy.frontend import root_view
        return root_view(request)

    def test_call_and_root_html_exists(self):
        request = testing.DummyRequest()
        resp = self._call_fut(request)
        assert resp.status_code == 200
        assert resp.body_file


class ViewsFunctionalTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.frontend import main
        from webtest import TestApp
        app = main({})
        self.testapp = TestApp(app)

    def test_static_view(self):
        resp = self.testapp.get('/static/root.html', status=200)
        assert '200' in resp.status

    def test_config_json_view(self):
        resp = self.testapp.get('/config.json', status=200)
        assert '200' in resp.status

    def test_embed_view(self):
        resp = self.testapp.get('/embed/XX', status=200)
        assert '200' in resp.status

    def test_register_view(self):
        resp = self.testapp.get('/register', status=200)
        assert '200' in resp.status
