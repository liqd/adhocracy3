"""Add or override py.test fixtures for all tests in this directory."""

from splinter import Browser
import pytest

from adhocracy.testing import splinter_browser_load_condition  # noqa


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
        pytest.skip('You need to enable embed test with --run_embed_tests')


@pytest.fixture()
def browser_embedder_root(browser, server_sample) -> Browser:
    """Start embedder application."""
    url = server_sample.application_url + 'frontend_static/embed.html'
    browser.visit(url)
    return browser
