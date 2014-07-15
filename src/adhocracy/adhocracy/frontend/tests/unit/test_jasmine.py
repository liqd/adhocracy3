import pytest
import time

from adhocracy.frontend.tests.unit.console import Parser
from adhocracy.frontend.tests.unit.console import Formatter


class TestJasmine:

    def test_all(self, browser_test):
        def jasmineFinished(browser):
            js = 'jsApiReporter.finished'
            return browser.evaluate_script(js)
        browser_test.wait_for_condition(jasmineFinished, 5)

        data = browser_test.evaluate_script('jsApiReporter.specs()')

        formatter = Formatter([])
        parser = Parser()
        results = parser.parse(data)
        formatter.results = results
        print(formatter.format())

        num_failures = len(list(results.failed()))
        assert num_failures == 0
