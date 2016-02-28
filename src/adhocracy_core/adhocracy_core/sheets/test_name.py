from pyramid import testing
from pytest import fixture
from pytest import mark


class TestNameSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.name import name_meta
        return name_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.name import IName
        from adhocracy_core.sheets.name import NameSchema
        from adhocracy_core.sheets import AnnotationRessourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == IName
        assert inst.meta.schema_class == NameSchema
        assert inst.meta.editable is False
        assert inst.meta.create_mandatory is True

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'name': ''}

    @mark.usefixtures('integration')
    def test_includeme_register_name_sheet(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)
