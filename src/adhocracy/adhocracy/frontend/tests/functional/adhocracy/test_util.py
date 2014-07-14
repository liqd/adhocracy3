import pytest
from time import sleep


class TestDeepCp:

    @pytest.fixture()
    def browser_root(self, browser, server_static):
        url = server_static.application_url + 'frontend_static/root.html'
        browser.visit(url)
        return browser

    @pytest.mark.parametrize("value",
                             [None,
                              {},
                              42,
                              {"foo": "bar"},
                              [None],
                              {'a': 3, 'b': None, 'c': [None]}
                              ])
    def test_deepcp(self, browser_root, value):
        sleep(1)
        code = """
               var U = require('Adhocracy/Util');
               return U.deepcp(input);
               """
        result = browser_root.evaluate_script_with_kwargs(code, input=value)
        assert result == value
