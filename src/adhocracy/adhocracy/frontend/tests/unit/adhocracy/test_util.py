from selenium import webdriver
from selenium.webdriver.common import proxy
from selenium.webdriver.support import wait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

import unittest


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


class TestDeepCp(unittest.TestCase):
    def setUp(self):
        self.driver = start_adh_session()

    def tearDown(self):
        self.driver.close()

    def _test_any(self, obj_in):
        obj_out = self.driver.execute_script(
            """
            var U = require('Adhocracy/Util');
            return U.deepcp(arguments[0]);
            """,
            obj_in);
        self.assertEqual(obj_in, obj_out)

    def test_null(self):
        self._test_any(None)

    def test_empty_obj(self):
        self._test_any({})

    def test_some_obj(self):
        self._test_any({u"a": 3, u"b": [None]})
