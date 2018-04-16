from pyramid import testing
from pyramid.config import Configurator
from pytest import raises
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_frontend')
    return config


@fixture
def config(request):
    """Return dummy testing configuration."""
    config = testing.setUp()
    config.include('tzf.pyramid_yml')
    config.config_defaults('adhocracy_frontend:defaults.yaml')
    request.addfinalizer(testing.tearDown)
    return config


@fixture(scope='class')
def functional():
    from webtest import TestApp
    config = Configurator(settings={})
    config.include('tzf.pyramid_yml')
    config.config_defaults('adhocracy_frontend:defaults.yaml')
    config.include('adhocracy_frontend')
    app = config.make_wsgi_app()
    return TestApp(app)


class TestConfigView:

    def call_fut(self, request):
        from . import config_view
        return config_view(request)

    def test_raise_if_no_config(self, request_):
        del request_.registry['config']
        with raises(KeyError):
            self.call_fut(request_)

    @mark.usefixtures('integration')
    def test_add_frontend_settings(self, request_):
        settings = request_.registry['config']
        config_json = self.call_fut(request_)
        assert settings.adhocracy.frontend.ws_url == config_json['ws_url']


class TestRootView:

    def call_fut(self, request):
        from . import root_view
        return root_view(request)

    def test_call_and_root_html_exists(self, request_):
        resp = self.call_fut(request_)
        assert resp.status_code == 200
        assert resp.body_file


class TestCustomCSSView:


    def call_fut(self, request):
        from . import custom_css_view
        return custom_css_view(request)

    def test_return_content_type_css(self, request_):
        resp = self.call_fut(request_)
        assert request_.response.content_type == 'text/css'

    def test_return_custom_css_from_config(self, config, request_):
        settings = request_.registry['config']
        settings.adhocracy.frontend.custom_css = '/*CSS*/'
        resp = self.call_fut(request_)
        assert resp == "/*CSS*/"

    def test_add_custom_css_view(self, functional):
        resp = functional.get('/static/custom.css', status=200)
        assert '200' in resp.status


class TestCustomStaticFolderView:

    @fixture
    def testfile(self, tmpdir):
        testfile = tmpdir.join("test.css")
        testfile.write('content')
        return testfile

    @fixture
    def functional_with_custom_static(self, testfile):
        from webtest import TestApp
        config = Configurator(settings={})
        config.include('tzf.pyramid_yml')
        config.config_defaults('adhocracy_frontend:defaults.yaml')
        settings = config.registry['config']
        settings.adhocracy.frontend.custom_static_folder = testfile.dirname
        config.include('adhocracy_frontend')
        app = config.make_wsgi_app()
        return TestApp(app)

    def test_add_static_view_if_custom_static(
            self, functional_with_custom_static, testfile):
        filename = testfile.basename
        resp = functional_with_custom_static.get('/static/custom/' + filename,
                                                 status=200)
        assert '200' in resp.status


class TestViewsFunctional:

    @mark.xfail(reason='asset build:/stylesheets/a3.css must exists')
    def test_static_view(self, functional ):
        resp = functional.get('/static/root.html', status=200)
        assert '200' in resp.status

    def test_config_json_view(self, functional):
        resp = functional.get('/config.json', status=200)
        assert '200' in resp.status

    @mark.xfail(reason='asset build:/stylesheets/a3.css must exists')
    def test_embed_view(self, functional):
        resp = functional.get('/embed/XX', status=200)
        assert '200' in resp.status

    @mark.xfail(reason='asset build:/stylesheets/a3.css must exists')
    def test_register_view(self, functional):
        resp = functional.get('/register', status=200)
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
