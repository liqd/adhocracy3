import pytest


class TestDeepCp:

    @pytest.mark.parametrize("value",
                             [None,
                              {},
                              42,
                              {"foo": "bar"},
                              [None],
                              {'a': 3, 'b': None, 'c': [None]}
                              ])
    def test_deepcp(self, browser_root, value):
        code = """
               var U = require('Adhocracy/Util');
               return U.deepcp(input);
               """
        result = browser_root.evaluate_script_with_kwargs(code, input=value)
        assert result == value
