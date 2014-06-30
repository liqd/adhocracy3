"""Public py.test fixtures."""
from webtest.http import StopableWSGIServer
from splinter import Browser
import pytest


@pytest.fixture(scope='class')
def app_sample(zeo, config, websocket):
    """Return the adhocracy wsgi application."""
    from adhocracy_sample import includeme
    includeme(config)
    return config.make_wsgi_app()


@pytest.fixture(scope='class')
def server_sample(request, app_sample) -> StopableWSGIServer:
    """Return a http server with the adhocracy_sample wsgi application."""
    server = StopableWSGIServer.create(app_sample)

    def fin():
        print('teardown adhocracy http server')
        server.shutdown()

    request.addfinalizer(fin)
    return server


@pytest.fixture()
def browser_sample_root(browser, server_sample) -> Browser:
    """Start sample application and go to the root html page."""
    url = server_sample.application_url + 'frontend_static/root.html'
    browser.visit(url)
    return browser
