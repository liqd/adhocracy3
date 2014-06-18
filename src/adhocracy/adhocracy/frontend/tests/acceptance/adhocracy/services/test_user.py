from selenium import webdriver
from selenium.webdriver.common import proxy
from selenium.webdriver.support import wait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

import unittest

import ipdb
#ipdb.set_trace()


def start_adh_session():
    capabilities = {
        "browserName": "firefox",
        "version": "",
        "platform": "ANY",
        "javascriptEnabled": True,
    }
    selenium_grid_url = "http://localhost:4444/wd/hub"
    driver = webdriver.Remote(desired_capabilities=capabilities, command_executor=selenium_grid_url)

    #waiter = wait.WebDriverWait(driver, 0.1)
    driver.set_page_load_timeout(15)
    driver.implicitly_wait(0.2)

    driver.get("http://lig:6541/frontend_static/root.html")
    assert "adhocracy root page" in driver.title

    return driver


class TestDirectiveLogin(unittest.TestCase):
    def setUp(self):
        self.driver = start_adh_session()
        self.good_user = {"name": "mr.nice", "password": "gandalf"}
        self.bad_user = {"name": "mr.evil", "password": "getoutofmyway"}

    def tearDown(self):
        self.driver.close()

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

    def test_login_success(self):
        self.assertTrue(self._test_login(self.good_user))

    def test_login_failure(self):
        self.assertFalse(self._test_login(self.bad_user))
