from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.document')


class TestDocumentSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.document import document_meta
        return document_meta

    def test_meta(self, meta):
        from adhocracy_core import sheets
        assert meta.isheet == sheets.document.IDocument
        assert meta.schema_class == sheets.document.DocumentSchema

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'title': '',
                              'description': '',
                              'elements': []}

    @mark.usefixtures('integration')
    def test_includeme_register_document_sheet(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestParagraphSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.document import paragraph_meta
        return paragraph_meta

    def test_meta(self, meta):
        from adhocracy_core import sheets
        assert meta.isheet == sheets.document.IParagraph
        assert meta.isheet.extends(sheets.document.ISection)
        assert meta.schema_class == sheets.document.ParagraphSchema

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'text': '',
                              'documents': []}

    @mark.usefixtures('integration')
    def test_includeme_register_document_sheet(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)
