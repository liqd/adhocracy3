"""Acceptances tests using py.test fixtures in :mod: `adhocracy.testing` and
   `adhocracy_sample.testing.
"""


class TestUserLogin:

    """User wants to login."""

    def _register(self, browser, server, name, email, password):
        register_url = server.application_url + 'register'
        browser.visit(register_url)
        fill_input(browser, '.register [name="username"]', name)
        fill_input(browser, '.register [name="email"]', email)
        fill_input(browser, '.register [name="password"]', password)
        fill_input(browser, '.register [name="password_repeat"]', password)
        click_button(browser, '.register [type="submit"]')

    def _login(self, browser, server, name_or_email, password,
               expect_success=True):
        login_url = server.application_url + 'frontend_static/root.html'
        browser.visit(login_url)
        fill_input(browser, '.login [name="nameOrEmail"]', name_or_email)
        fill_input(browser, '.login [name="password"]', password)
        click_button(browser, '.login [type="submit"]')
        if expect_success:
            browser.wait_for_condition(is_logged_in, 2)

    def _logout(self, browser):
        click_button(browser, '.user-indicator-logout')

    def test_login_username(self, browser, server):
        self._register(browser, server, 'user1', 'email1@example.com',
                       'password1')
        self._logout(browser)
        # FIXME: Test that no error messages are shown
        self._login(browser, server, 'user1', 'password1')
        assert is_logged_in(browser)

    def test_login_email(self, browser, server):
        self._register(browser, server, 'user2', 'email2@example.com',
                       'password2')
        self._logout(browser)
        self._login(browser, server, 'email2@example.com', 'password2')
        assert is_logged_in(browser)

    def test_login_error(self, browser, server):
        self._register(browser, server, 'user3', 'email3@example.com',
                       'password3')
        self._logout(browser)
        self._login(browser, server, 'user3', 'other',
                    expect_success=False)
        assert browser.is_element_present_by_css(
            '.login .form-error:not(.ng-hide)')
        assert not is_logged_in(browser)

    def test_register_error(self, browser, server):
        register_url = server.application_url + 'register'
        browser.visit(register_url)
        fill_input(browser, '.register [name="username"]', 'user4')
        fill_input(browser, '.register [name="email"]', 'email4@example.com')
        fill_input(browser, '.register [name="password"]', 'pass4')
        fill_input(browser, '.register [name="password_repeat"]', 'other')

        assert browser.is_element_present_by_css(
            '.register [type="submit"]:disabled')

    def test_login_persistence(self, browser, server):
        self._register(browser, server, 'user5', 'email5@example.com',
                       'password5')
        self._logout(browser)
        self._login(browser, server, 'user5', 'password5')
        browser.reload()
        assert is_logged_in(browser)


def fill_input(browser, selector, value):
    element = browser.browser.find_by_css(selector).first
    element.fill(value)


def click_button(browser, selector):
    element = browser.browser.find_by_css(selector).first
    element.click()


def is_logged_in(browser_root):
    return browser_root.browser.is_element_present_by_css('.user-indicator-logout')
