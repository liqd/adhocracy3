import json
import pytest


def compile_js_code(body, **kwargs):
    """Generate a single JavaScript expression from complex code.

    This is accomplished by wrapping the code in a JavaScript function
    and passing any key word arguments to that function.  All arguments
    will be JSON encoded.

    :param body: any JavaScript code
    :param kwargs: arguments that will be passed to the wrapper function

    :returns: a string containing a single JavaScript expression suitable
        for consumption by splinter's ``evaluate_script``

    >>> code = "var a = 1; test.y = a; return test;"
    >>> compile_js_code(code, test={"x": 2})
    '(function(test) {var a = 1; test.y = a; return test;})({"x": 2})'

    """
    # make sure keys and values are in the same order
    keys = []
    values = []
    for key in kwargs:
        keys.append(key)
        values.append(kwargs[key])

    keys = ', '.join(keys)
    values = ', '.join((json.dumps(v) for v in values))

    return "(function({}) {{{}}})({})".format(keys, body, values)


class TestDeepCp:

    @pytest.fixture()
    def browser_root(self, browser, server_sample):
        url = server_sample.application_url + 'frontend_static/root.html'
        browser.visit(url)
        # The splinter browser has no general "wait for page load" function:
        # https://github.com/cobrateam/splinter/issues/237
        def is_page_loaded(browser):
            code = 'document.readyState === "complete";'
            return browser.evaluate_script(code)
        browser.wait_for_condition(is_page_loaded, 5)
        return browser

    @pytest.mark.parametrize("input,expected",
                             [(None, None),
                              ({}, {}),
                              (42, 42),
                              ({"foo": "bar"}, {"foo": "bar"}),
                              ([None], [None]),
                              ])
    def test_deepcp(self, browser_root, input, expected):
        body = """
               var U = require('Adhocracy/Util');
               return U.deepcp(input);
               """
        code = compile_js_code(body, input=input)
        result = browser_root.evaluate_script(code)
        assert result == expected
