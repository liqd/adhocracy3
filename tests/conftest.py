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
def server_sample(request, app_sample) -> StopableWSGIServer:
    """Return a http server with the sample adhocracy wsgi application."""
    server = StopableWSGIServer.create(app_sample)
    request.addfinalizer(server.shutdown)
    return server


@fixture
def browser(browser, server_sample) -> Browser:
    """Return test browser, start sample application and go to `root.html`.

    Add attribute `root_url` pointing to the adhocracy root.html page.
    Add attribute `app_url` pointing to the adhocracy application page.
    Before visiting a new url the browser waits until the angular app is loaded
    """
    from adhocracy.testing import angular_app_loaded
    app_url = server_sample.application_url
    browser.root_url = app_url + 'frontend_static/root.html'
    browser.app_url = app_url
    browser.visit(browser.root_url)
    browser.wait_for_condition(angular_app_loaded, 5)
    return browser


@fixture
def browser_embed(browser, server_sample) -> Browser:
    """Start embedder application."""
    url = server_sample.application_url + 'frontend_static/embed.html'
    browser.visit(url)
    return browser
