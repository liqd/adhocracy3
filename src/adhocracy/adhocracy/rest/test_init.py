from colander import _null
from pyramid import testing

import unittest


class ColanderNullJsonAdapterUnitTest(unittest.TestCase):

    def test_valid_colander_null(self):
        from . import colander_null_json_adapter
        request = testing.DummyRequest()
        context = _null()
        assert colander_null_json_adapter(context, request) is None

    def test_valid_non_colander_null(self):
        from . import colander_null_json_adapter
        request = testing.DummyRequest()
        context = {}
        assert isinstance(colander_null_json_adapter(context, request), object)
