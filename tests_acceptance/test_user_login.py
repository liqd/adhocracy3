import time

from splinter import Browser
import pytest


class TestUserLogin:

    """User wants to login."""

    @pytest.fixture()
    def browser_root(self, browser, server_sample) -> Browser:
        """Start sample application and go to the root html page."""
        url = server_sample.application_url + 'frontend_static/root.html'
        browser.visit(url)
        return browser

    def test_login_valid(self, browser_root):
        fill_input(browser_root, '.login [name="password"]', 'password')
        fill_input(browser_root, '.login [name="name"]', 'name')
        click_button(browser_root, '.login [type="submit"]')
        assert is_logged_in(browser_root)


def fill_input(browser_root, selector, value):
    element = browser_root.browser.find_by_css(selector).first
    element.fill(value)


def click_button(browser_root, selector):
    element = browser_root.browser.find_by_css(selector).first
    element.click()


def is_logged_in(browser_root):
    return browser_root.browser.is_element_present_by_css('.logout')
