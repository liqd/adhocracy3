import unittest

from pyramid import testing

from adhocracy.utils import get_sheet


class NameDummySheetIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy_sample.sheets.sample_sheets')

    def tearDown(self):
        testing.tearDown()

    def test_create_name_dummy_sheet(self):
        from adhocracy.sheets.name import IName
        from adhocracy_sample.sheets.sample_sheets import DummyNameSheet
        context = testing.DummyResource(__provides__=IName)
        inst = get_sheet(context, IName)
        assert isinstance(inst, DummyNameSheet)

    def test_create_name_extended_sheet(self):
        from adhocracy_sample.sheets.sample_sheets import IExtendedName
        context = testing.DummyResource(__provides__=IExtendedName)
        inst = get_sheet(context, IExtendedName)
        appstruct = inst.get()
        assert 'description_x' in appstruct
