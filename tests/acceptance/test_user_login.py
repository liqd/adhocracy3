"""Acceptances tests using py.test fixtures in :mod: `adhocracy.testing` and
   `adhocracy_sample.testing.
"""


class TestUserLogin:

    """User wants to login."""

    def test_login_valid(self, browser_sample_root):
        fill_input(browser_sample_root, '.login [name="password"]', 'password')
        fill_input(browser_sample_root, '.login [name="name"]', 'name')
        click_button(browser_sample_root, '.login [type="submit"]')
        assert is_logged_in(browser_sample_root)


def fill_input(browser, selector, value):
    element = browser.browser.find_by_css(selector).first
    element.fill(value)


def click_button(browser, selector):
    element = browser.browser.find_by_css(selector).first
    element.click()


def is_logged_in(browser_root):
    return browser_root.browser.is_element_present_by_css('.logout')
