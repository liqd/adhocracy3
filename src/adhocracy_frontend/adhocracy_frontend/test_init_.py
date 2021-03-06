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

    def test_add_css(self, request_):
        request_.cachebusted_url = lambda x: 'cb:' + x
        resp = self.call_fut(request_)
        assert 'cb:adhocracy_frontend:build/stylesheets/a3.css' in resp['css']

    def test_ignore_custom_css_if_disabled(self, mocker, request_):
        request_.cachebusted_url = lambda x: 'cb:' + x
        mocker.patch('adhocracy_frontend._get_custom_css_folder',
                     autospec=True, return_value='')
        resp = self.call_fut(request_)
        assert 'cb:static/custom/main.css' not in resp['css']

    def test_add_custom_css_if_enabled(self, mocker, request_):
        request_.cachebusted_url = lambda x: 'cb:' + x
        mocker.patch('adhocracy_frontend._get_custom_css_folder',
                     autospec=True, return_value='/static/custom')
        resp = self.call_fut(request_)
        assert 'cb:/static/custom/main.css' in resp['css']


class TestCustomStaticFolderView:

    @fixture
    def maincss(self, tmpdir):
        testfile = tmpdir.join("main.css")
        testfile.write('content')
        return testfile

    @fixture
    def functional_with_custom_static(self, maincss):
        from webtest import TestApp
        config = Configurator(settings={})
        config.include('tzf.pyramid_yml')
        config.config_defaults('adhocracy_frontend:defaults.yaml')
        settings = config.registry['config']
        settings.adhocracy.frontend.custom_static_folder = maincss.dirname
        config.include('adhocracy_frontend')
        app = config.make_wsgi_app()
        return TestApp(app)

    def test_ignoreadd_static_view_if_custom_main_css(
            self, functional, maincss):
        filename = maincss.basename
        resp = functional.get('/static/custom/' + filename, status=404)
        assert '404' in resp.status

    def test_add_static_view_if_custom_main_css(
            self, functional_with_custom_static, maincss):
        filename = maincss.basename
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
