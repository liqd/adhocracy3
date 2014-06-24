from splinter import Browser
import pytest


# REVIEW: the elements that we interact with should be identified by
# name or class, not by angular directives or parameters to angular directives.
# Those are implementation details and are likely to change while the names
# and classes are part of a public API that is also used for CSS and is
# therefore more or less stable.

class TestUserLogin:

    """User wants to login."""

    @pytest.fixture()
    def browser_root(self, browser, server_sample) -> Browser:
        """Start sample application and go to the root html page."""
        url = server_sample.application_url + 'frontend_static/root.html'
        browser.visit(url)
        return browser

    def test_login_valid(self, browser_root):
        fill_input(browser_root, 'credentials.password', 'password')
        fill_input(browser_root, 'credentials.name', 'name')
        click_button(browser_root, 'logIn()')
        assert is_logged_in(browser_root)

    # REVIEW: this test currently fails
    def test_login_non_valid(self, browser_root):
        fill_input(browser_root, 'credentials.password', 'getoutofmyway')
        fill_input(browser_root, 'credentials.name', 'mr.evil')
        click_button(browser_root, 'logIn()')
        assert not is_logged_in(browser_root)


def fill_input(browser_root, ng_model_attr, value):
        xpath = '//input[contains(@ng-model, "{0}")]'.format(ng_model_attr)
        element = browser_root.browser.find_by_xpath(xpath).first
        element.fill(value)


def click_button(browser_root, ng_click_attr):
        xpath = '//input[contains(@ng-click, "{0}")]'.format(ng_click_attr)
        element = browser_root.browser.find_by_xpath(xpath).first
        element.click()


def is_logged_in(browser_root):
    return browser_root.browser.is_element_present_by_value('LogOut')
