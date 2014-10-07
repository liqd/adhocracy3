"""User wants to register and login"""
from pytest import fixture

from adhocracy_core.testing import god_email
from adhocracy_core.testing import god_name
from adhocracy_core.testing import god_password

from .shared import fill_input
from .shared import click_button
from .shared import login
from .shared import logout
from .shared import login_god
from .shared import is_logged_in


@fixture
def browser(browser):
    logout(browser)
    return browser


class TestUserLogin:

    def test_register(self, browser):
        register(browser, 'user2', 'email2@example.com', 'password2',
                 expect_success=False)
        assert is_not_yet_activated(browser)

    def test_login_email(self, browser):
        login(browser, god_email, god_password)
        assert is_logged_in(browser)

    def test_login_name(self, browser):
        logout(browser)
        login(browser, god_name, god_password)
        assert is_logged_in(browser)

    def test_login_error(self, browser):
        login(browser, 'wrong', 'wrong', expect_success=False, visit_root=False)
        assert browser.is_element_present_by_css(
            '.login .form-error:not(.ng-hide)', wait_time=2)
        assert not is_logged_in(browser)

    def test_register_error_wrong_password_repeat(self, browser):
        register(browser, 'user4', 'email4@example.com', 'password4',
                 'wrong_repeated_password', expect_success=False)
        assert browser.browser.is_element_present_by_css(
            '.register [type="submit"]:disabled', wait_time=1)

    def test_login_persistence(self, browser):
        login_god(browser)
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
