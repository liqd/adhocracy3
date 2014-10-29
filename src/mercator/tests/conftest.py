"""Add or override py.test fixtures for all tests in this directory."""
from splinter import Browser
from pytest import fixture


@fixture(scope='class')
def browser(browser_root, backend, frontend, frontend_url) -> Browser:
    """Return test browser, start application and go to `root.html`."""
    return browser_root
