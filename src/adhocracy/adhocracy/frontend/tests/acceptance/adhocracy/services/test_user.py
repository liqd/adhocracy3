from selenium import webdriver
from selenium.webdriver.common import proxy
from selenium.webdriver.support import wait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

import unittest


def rtest_login_success(server_sample, browser):
    url = server_sample.application_url + 'frontend_static/root.html'
    browser.visit(url)
    # TODO ...
    #browser.browser.fill_form({'credentials.name': 'mr.nice',
    #                           'credentials.password': 'gandalf'})
    #import ipdb; ipdb.set_trace()


class TestDirectiveLogin(unittest.TestCase):
    def setUp(self):
        self.bad_user = {"name": "mr.evil", "password": "getoutofmyway"}

    def _test_login(self, user):
        time.sleep(0.8)  # FIXME: there are better ways!

        # attempt login
        directive = self.driver.find_element_by_xpath('//adh-login')
        name = directive.find_element_by_xpath("//input[contains(@ng-model,'credentials.name')]")
        password = directive.find_element_by_xpath("//input[contains(@ng-model,'credentials.password')]")
        button = directive.find_element_by_xpath("//input[contains(@ng-click,'logIn()')]")

        name.send_keys(user['name'])
        password.send_keys(user['password'])
        button.click()

        # check if login succeeded
        try:
            time.sleep(0.8)  # FIXME: there are better ways!
            directive.find_element_by_xpath("//span[text()='"+user['name']+"']")  # FIXME: user['name'] must be checked for "'"
            directive.find_element_by_xpath("//input[contains(@ng-click,'logOut()')]")
        except NoSuchElementException:
            return False

        return True

    def rtest_login_failure(self):
        self.assertFalse(self._test_login(self.bad_user))
