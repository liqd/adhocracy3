import unittest

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


@fixture
def integration(config):
    config.include('tzf.pyramid_yml')
    config.config_defaults('adhocracy_frontend:defaults.yaml')
    config.include('adhocracy_frontend')
    return config


class TestConfigView:

    @fixture
    def config(self, request):
        """Return dummy testing configuration."""
        config = testing.setUp()
        config.include('tzf.pyramid_yml')
        config.config_defaults('adhocracy_frontend:defaults.yaml')
        request.addfinalizer(testing.tearDown)
        return config

    def call_fut(self, request):
        from adhocracy_frontend import config_view
        return config_view(request)

    def test_raise_if_no_config(self, request_):
        del request_.registry['config']
        with raises(KeyError):
            self.call_fut(request_)

    @mark.usefixtures('integration')
    def test_add_frontend_settings(self, request_):
        settings = request_.registry['config']
        config_json = self.call_fut(request_)
        assert settings.adhocracy.ws_url == config_json['ws_url']


class RootViewTest(unittest.TestCase):

    def call_fut(self, request):
        from adhocracy_frontend import root_view
        return root_view(request)

    def test_call_and_root_html_exists(self):
        request = testing.DummyRequest(scheme='https')
        resp = self.call_fut(request)
        assert resp.status_code == 200
        assert resp.body_file


@mark.usefixtures('functional')
class ViewsFunctionalTest:

    @mark.xfail(reason='asset build:/stylesheets/a3.css must exists')
    def test_static_view(self):
        resp = self.testapp.get('/static/root.html', status=200)
        assert '200' in resp.status

    def test_config_json_view(self):
        resp = self.testapp.get('/config.json', status=200)
        assert '200' in resp.status

    @mark.xfail(reason='asset build:/stylesheets/a3.css must exists')
    def test_embed_view(self):
        resp = self.testapp.get('/embed/XX', status=200)
        assert '200' in resp.status

    @mark.xfail(reason='asset build:/stylesheets/a3.css must exists')
    def test_register_view(self):
        resp = self.testapp.get('/register', status=200)
        assert '200' in resp.status


@mark.usefixtures('integration')
class TestIntegrationIncludeme:

    def test_includeme(self, integration):
        """Check that includeme runs without errors and config is loaded."""
        assert integration.registry['config']

    def test_register_subscriber(self, registry):
        from . import add_cors_headers
        handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
        assert add_cors_headers.__name__ in handlers


class TestConfig:

    @fixture
    def config(self, config):
        config.include('tzf.pyramid_yml')
        config.config_defaults('adhocracy_frontend:test_config.yaml')
        return config

    def test_config_file_set_default_values(self, config):
        settings = config.registry['config']
        assert settings.setting == 'test'

    def test_additional_config_files_extend_defaul_values(self, config):
        config.config_defaults('adhocracy_frontend:test_config.yaml, '
            'adhocracy_frontend:test_config_extended.yaml')
        settings = config.registry['config']
        assert settings.setting == 'test'
        assert settings.setting_extended == 'extended'

    @mark.parametrize("setting, typ", [('setting_str', str),
                                       ('setting_bool', bool),
                                       ('setting_int', int),
                                       ('setting_float', float),
                                       ])
    def test_values_are_typed(self, setting, typ, config):
        settings = config.registry['config']
        assert isinstance(settings[setting], typ)
