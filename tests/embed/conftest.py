"""Add or override py.test fixtures for all tests in this directory."""

from splinter import Browser
import pytest

from adhocracy.testing import splinter_browser_load_condition  # noqa


@pytest.fixture()
def browser_embedder_root(browser, server_sample) -> Browser:
    """Start embedder application."""
    url = 'http://adhocracy.embedder.gaa:6541/frontend_static/embed.html'
    browser.visit(url)
    return browser
