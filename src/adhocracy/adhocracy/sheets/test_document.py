import unittest

from pyramid import testing

from adhocracy.utils import get_sheet


class DocumentSheetIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.document')

    def tearDown(self):
        testing.tearDown()

    def test_includeme_add_document_sheet_to_registry(self):
        from adhocracy.sheets.document import IDocument
        context = testing.DummyResource(__provides__=IDocument)
        inst = get_sheet(context, IDocument)
        assert inst.meta.isheet is IDocument
