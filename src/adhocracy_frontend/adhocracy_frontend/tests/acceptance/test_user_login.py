"""User wants to register and login"""

from adhocracy_core.testing import god_email
from adhocracy_core.testing import god_login
from adhocracy_core.testing import god_password

from adhocracy_frontend.tests.acceptance.shared import fill_input
from adhocracy_frontend.tests.acceptance.shared import click_button
from adhocracy_frontend.tests.acceptance.shared import login
from adhocracy_frontend.tests.acceptance.shared import logout
from adhocracy_frontend.tests.acceptance.shared import is_logged_in
from adhocracy_frontend.tests.acceptance.shared import get_random_string

USER = get_random_string(n=5)
MAIL = "%s@mail.info" % USER
PASSWORD = "password"


class TestUserLogin:

    def test_register(self, browser):
        register(browser, USER, MAIL, PASSWORD, expect_success=False)
        assert is_not_yet_activated(browser)

    def test_no_login_without_activation(self, browser):
        login(browser, USER, PASSWORD, expect_success=False, visit_root=False)
        assert browser.is_text_present("User account not yet activated")
        assert not is_logged_in(browser)

    def test_register_error_wrong_password_repeat(self, browser):
        register(browser, 'user4', 'email4@example.com', 'password4',
                 'wrong_repeated_password', expect_success=False)
        assert browser.browser.is_element_present_by_css(
            '.register [type="submit"]:disabled')

    def test_login_name_with_wrong_name(self, browser):
        login(browser, 'wrong', god_password, expect_success=False, visit_root=False)
        assert browser.is_element_present_by_css(
            '.login .form-error:not(.ng-hide)')
        assert not is_logged_in(browser)

    def login_name_with_wrong_password(self, browser):
        login(browser, god_login, 'wrong', expect_success=False, visit_root=False)
        assert browser.is_element_present_by_css(
            '.login .form-error:not(.ng-hide)', wait_time=2)
        assert not is_logged_in(browser)

    def login_name_with_password_length_lower_6(self, browser):
        login(browser, god_login, 'short', expect_success=False, visit_root=False)
        browser.is_text_present('password to short')
        assert not is_logged_in(browser)

    def test_login_name(self, browser):
        login(browser, god_login, god_password)
        assert is_logged_in(browser)

    def test_login_email(self, browser):
        logout(browser)
        login(browser, god_email, god_password)
        assert is_logged_in(browser)

    def test_login_persistence(self, browser):
        browser.reload()
        assert is_logged_in(browser)


def register(browser, name, email, password, repeated_password=None,
             expect_success=True):
    register_url = browser.app_url + 'register'
    browser.visit(register_url)
    fill_input(browser, '.register [name="username"]', name)
    fill_input(browser, '.register [name="email"]', email)
    fill_input(browser, '.register [name="password"]', password)
    fill_input(browser, '.register [name="password_repeat"]',
               repeated_password or password)
    click_button(browser, '.register [type="submit"]')
    if expect_success:
        browser.wait_for_condition(is_logged_in, 2)


def is_not_yet_activated(browser):
    return browser.is_element_present_by_css('.register-success')
