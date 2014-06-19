"""Public py.test fixtures."""

from webtest.http import StopableWSGIServer
import pytest


@pytest.fixture()
def app_sample(zeo, config):
    """Return the adhocracy wsgi application."""
    from adhocracy_sample import includeme
    includeme(config)
    return config.make_wsgi_app()


@pytest.fixture()
def server_sample(app_sample, request) -> StopableWSGIServer:
    """Return a http server with the adhocracy_sample wsgi application."""
    server = StopableWSGIServer.create(app_sample)

    def fin():
        print('teardown adhocracy http server')
        server.shutdown()

    request.addfinalizer(fin)
    return server
