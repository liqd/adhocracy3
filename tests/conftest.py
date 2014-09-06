"""Add or override py.test fixtures for all tests in this directory."""
from splinter import Browser
from pytest import fixture
from pytest import skip
from webtest.http import StopableWSGIServer


def pytest_addoption(parser):
    """Add pytest option --run_embed_tests."""
    parser.addoption('--run_embed_tests', action='store_true', default=False,
                     help='run embed tests (needs /etc/hosts modifications)',
                     )


def pytest_runtest_setup(item):
    """Skip tests with `embed` marker if `--run_embed_tests` is not set."""
    run_embed = item.config.getoption('--run_embed_tests')
    embed_marker = item.get_marker('embed')
    if run_embed:
        return
    elif embed_marker:
        skip('You need to enable embed test with --run_embed_tests')


@fixture(scope='class')
def frontend_with_backend(request, backend_sample):
    """Return the frontend http server and start the backend sample server."""
    from pyramid.config import Configurator
    from adhocracy_frontend import includeme
    settings = {'adhocracy.frontend.rest_url': backend_sample.application_url,
                }
    config = Configurator(settings=settings)
    includeme(config)
    app = config.make_wsgi_app()
    server = StopableWSGIServer.create(app)
    request.addfinalizer(server.shutdown)
    return server


@fixture
def browser(browser, frontend_with_backend) -> Browser:
    """Return test browser, start sample application and go to `root.html`.

    Add attribute `root_url` pointing to the adhocracy root.html page.
    Add attribute `app_url` pointing to the adhocracy application page.
    Before visiting a new url the browser waits until the angular app is loaded
    """
    from adhocracy_frontend.testing import angular_app_loaded
    app_url = frontend_with_backend.application_url
    browser.root_url = app_url
    browser.app_url = app_url
    browser.visit(browser.root_url)
    browser.wait_for_condition(angular_app_loaded, 5)
    return browser


@fixture
def browser_embed(browser, frontend_with_backend) -> Browser:
    """Start embedder application."""
    url = frontend_with_backend.application_url + 'static/embed.html'
    browser.visit(url)
    return browser
