from time import sleep

import pytest

from console import Parser
from console import Formatter

class TestJasmine:

    @pytest.fixture()
    def browser_test(self, browser, server_sample):
        url = server_sample.application_url + 'frontend_static/test.html'
        browser.visit(url)
        return browser

    def test_all(self, browser_test):
        def jasmineFinished():
            js = 'jsApiReporter.finished'
            return browser_test.evaluate_script(js)
        browser_test.wait_for_condition(jasmineFinished(), 5)
        data = browser_test.evaluate_script('jsApiReporter.specs()')

        formatter = Formatter([])
        parser = Parser()
        results = parser.parse(data)
        formatter.results = results
        print(formatter.format())

        assert len(list(results.failed())) == 0
