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
def backend_sample(request, app_sample):
    """Return a http server with the adhocracy wsgi application."""
    server = StopableWSGIServer.create(app_sample)
    request.addfinalizer(server.shutdown)
    return server
