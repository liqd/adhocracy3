import pytest


class TestDeepCp:

    @pytest.fixture()
    def browser_root(self, browser, server_sample):
        url = server_sample.application_url + 'frontend_static/root.html'
        browser.visit(url)
        return browser

    def _call_fut(self, browser, obj_in):
        code ="""
        var U = require('Adhocracy/Util');
        U.deepcp({0});
        """.format(str(obj_in))
        return browser.evaluate_script(code)

    def test_equal(self, browser_root):
        value = None
        assert self._call_fut(browser_root, value) == value

    def test_empty_obj(self, browser_root):
        value = {}
        assert self._call_fut(browser_root, value) == value

    # deactivated: webdriver swallows trailing null values in
    # javascript arrays, so this test breaks.  FIXME: need to fix
    # webdriver or find a work-around.  we need to be able to pass
    # arrays!
    #def test_some_obj(self):
    #    value = {'a': 3, 'b': None, 'c': [None]}
    #    assert self._call_fut(value) == value
