from pyramid import testing
from pytest import fixture


class TestTitleSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.title import title_meta
        return title_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.title import ITitle
        from adhocracy_core.sheets.title import TitleSchema
        from adhocracy_core.sheets import AnnotationRessourceSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == ITitle
        assert inst.meta.schema_class == TitleSchema
        assert inst.meta.editable is True
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'title': ''}


def test_includeme_register_title_sheet(config):
    from adhocracy_core.sheets.title import ITitle
    from adhocracy_core.utils import get_sheet
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.title')
    context = testing.DummyResource(__provides__=ITitle)
    inst = get_sheet(context, ITitle)
    assert inst.meta.isheet is ITitle
