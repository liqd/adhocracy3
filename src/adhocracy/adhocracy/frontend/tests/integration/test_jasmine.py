import pytest

# this is structurally equivalent to ../unit/test_jasmine.py, but
# it runs igtest.html instead of test.html

from adhocracy.frontend.tests.unit.console import Parser
from adhocracy.frontend.tests.unit.console import Formatter

pytestmark = pytest.mark.jasmine

class TestJasmine:
    def test_all(self, browser_igtest):
        data = browser_igtest.evaluate_script('jsApiReporter.specs()')

        formatter = Formatter([])
        parser = Parser()
        results = parser.parse(data)
        formatter.results = results
        print(formatter.format())

        num_failures = len(list(results.failed()))
        assert num_failures == 0
