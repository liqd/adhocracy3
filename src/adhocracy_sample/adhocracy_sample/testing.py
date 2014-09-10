"""Public py.test fixtures."""
from pytest import fixture
from webtest.http import StopableWSGIServer


@fixture(scope='class')
def app_sample(zeo, settings, websocket):
    """Return the adhocracy sample wsgi application."""
    from pyramid.config import Configurator
    import adhocracy_sample
    configurator = Configurator(settings=settings,
                                root_factory=adhocracy_sample.root_factory)
    configurator.include(adhocracy_sample)
    app = configurator.make_wsgi_app()
    return app


@fixture(scope='class')
def backend_sample(request, ws_settings, app_sample):
    """Return a http server with the adhocracy wsgi application."""
    rest_url = ws_settings['rest_url']
    port = rest_url.split(':')[2]
    server = StopableWSGIServer.create(app_sample, port=port)
    request.addfinalizer(server.shutdown)
    return server
