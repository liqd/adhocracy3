import pytest

# override default fixtures
from adhocracy.testing import splinter_browser_load_condition
from adhocracy.testing import browser_instance


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
