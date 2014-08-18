import pytest

from adhocracy.frontend.tests.unit.console import Parser
from adhocracy.frontend.tests.unit.console import Formatter


pytestmark = pytest.mark.jasmine  # mark theses tests as jasmine tests


class TestJasmine:

    # phantomjs does not provide Function.prototype.bind:
    # https://github.com/ariya/phantomjs/issues/10522
    # a3 provides a poly-fill to deal with this (see commit c0d0cd3).

    def test_all(self, browser_test):
        data = browser_test.evaluate_script('jsApiReporter.specs()')

        formatter = Formatter([])
        parser = Parser()
        results = parser.parse(data)
        formatter.results = results
        print(formatter.format())

        num_failures = len(list(results.failed()))
        assert num_failures == 0
