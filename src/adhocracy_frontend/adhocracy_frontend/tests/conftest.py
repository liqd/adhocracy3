"""Add or override py.test fixtures for all tests in this directory."""
from splinter import Browser
from pytest import fixture
from pytest import skip


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
def browser(browser_root, backend, frontend, frontend_url) -> Browser:
    """Return test browser, start application and go to `root.html`."""
    return browser_root


@fixture
def rest_url(settings) -> str:
    """Return URL of REST API."""
    return 'http://%s:%s/' % (settings['host'], settings['port'])
