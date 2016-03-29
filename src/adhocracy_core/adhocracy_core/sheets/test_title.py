from pyramid import testing
from pytest import fixture
from pytest import mark


class TestTitleSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.title import title_meta
        return title_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.title import ITitle
        from adhocracy_core.sheets.title import TitleSchema
        from adhocracy_core.sheets import AnnotationRessourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == ITitle
        assert inst.meta.schema_class == TitleSchema
        assert inst.meta.editable is True
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'title': ''}

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)

