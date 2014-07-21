"""Acceptances tests using py.test fixtures in :mod: `adhocracy.testing` and
   `adhocracy_sample.testing.
"""


class TestUserLogin:

    """User wants to login."""

    def _register(self, browser, server_sample, name, email, password):
        register_url = server_sample.application_url + 'register'
        browser.visit(register_url)
        fill_input(browser, '.register [name="username"]', name)
        fill_input(browser, '.register [name="email"]', email)
        fill_input(browser, '.register [name="password"]', password)
        fill_input(browser, '.register [name="password_repeat"]', password)
        click_button(browser, '.register [type="submit"]')

    def _login(self, browser, server_sample, name_or_email, password):
        # REVIEW: Now, as register automatically redirects here, it is
        # confusing to repeat the redirect in the test
        login_url = server_sample.application_url + 'frontend_static/root.html'
        browser.visit(login_url)
        fill_input(browser, '.login [name="nameOrEmail"]', name_or_email)
        fill_input(browser, '.login [name="password"]', password)
        click_button(browser, '.login [type="submit"]')

    def test_login_username(self, browser, server_sample):
        self._register(browser, server_sample, 'user1', 'email1@example.com',
                       'password1')
        # FIXME: Test that no error messages are shown
        self._login(browser, server_sample, 'user1', 'password1')
        assert is_logged_in(browser)

    def test_login_email(self, browser, server_sample):
        self._register(browser, server_sample, 'user1', 'email1@example.com',
                       'password1')
        self._login(browser, server_sample, 'email1@example.com', 'password1')
        assert is_logged_in(browser)

    def test_login_error(self, browser, server_sample):
        self._register(browser, server_sample, 'user1', 'email1@example.com',
                       'password1')
        self._login(browser, server_sample, 'user1', 'password2')
        assert browser.is_element_present_by_css(
            '.login .form-error:not(.ng-hide)')
        assert not is_logged_in(browser)

    def test_register_error(self, browser, server_sample):
        register_url = server_sample.application_url + 'register'
        browser.visit(register_url)
        fill_input(browser, '.register [name="username"]', 'user2')
        fill_input(browser, '.register [name="email"]', 'email2@example.com')
        fill_input(browser, '.register [name="password"]', 'pass2')
        fill_input(browser, '.register [name="password_repeat"]', 'otherpass')

        assert browser.is_element_present_by_css(
            '.register [type="submit"]:disabled')

    def test_login_persistence(self, browser, server_sample):
        self._register(browser, server_sample, 'user1', 'email1@example.com',
                       'password1')
        self._login(browser, server_sample, 'user1', 'password1')
        browser.reload()
        assert is_logged_in(browser)


def fill_input(browser, selector, value):
    element = browser.browser.find_by_css(selector).first
    element.fill(value)


def click_button(browser, selector):
    element = browser.browser.find_by_css(selector).first
    element.click()


def is_logged_in(browser_root):
    return browser_root.browser.is_element_present_by_css('.logout')
