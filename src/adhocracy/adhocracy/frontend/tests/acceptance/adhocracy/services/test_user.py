import pytest


@pytest.fixture()
def browser_root(browser, server_sample):
    url = server_sample.application_url + 'frontend_static/root.html'
    browser.visit(url)
    return browser


class TestUserLogin:

    def test_login_valid(self, browser_root):
        fill_input(browser_root, 'credentials.password', 'password')
        fill_input(browser_root, 'credentials.name', 'name')
        click_button(browser_root, 'logIn()')
        assert is_logged_in(browser_root)

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
