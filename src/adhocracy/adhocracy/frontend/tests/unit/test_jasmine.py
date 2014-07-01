import pytest

from adhocracy.frontend.tests.unit.console import Parser
from adhocracy.frontend.tests.unit.console import Formatter


class TestJasmine:

    @pytest.fixture()
    def browser_test(self, browser, server_static):
        url = server_static.application_url + 'frontend_static/test.html'
        browser.visit(url)
        return browser

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

        assert len(list(results.failed())) == 0
