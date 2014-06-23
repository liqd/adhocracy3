import pytest


class TestDeepCp:

    @pytest.fixture()
    def browser_root(self, browser, server_sample):
        url = server_sample.application_url + 'frontend_static/root.html'
        browser.visit(url)
        return browser

    @pytest.mark.parametrize("input,expected",
                             [(None, None),
                              ({}, {}),
                              ])
    def test_deepcp(self, browser_root, input, expected):
        code = """
               var U = require('Adhocracy/Util');
               U.deepcp({0});
               """.format(input)
        result = browser_root.browser.evaluate_script(code)
        assert result == expected

    # deactivated: webdriver swallows trailing null values in
    # javascript arrays, so this test breaks.  FIXME: need to fix
    # webdriver or find a work-around.  we need to be able to pass
    # arrays!
    #def test_some_obj(self):
    #    value = {'a': 3, 'b': None, 'c': [None]}
    #    assert self._call_fut(value) == value
