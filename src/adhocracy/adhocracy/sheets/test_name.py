import unittest

from pyramid import testing

from adhocracy.utils import get_sheet


class NameSheetIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.name')

    def tearDown(self):
        testing.tearDown()

    def test_includeme_add_name_sheet_to_registry(self):

        from adhocracy.sheets.name import IName
        context = testing.DummyResource(__provides__=IName)
        inst = get_sheet(context, IName)
        assert inst.meta.isheet is IName
