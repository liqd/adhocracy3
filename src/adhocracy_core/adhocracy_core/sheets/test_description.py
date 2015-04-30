from pyramid import testing
from pytest import fixture


class TestDescriptionSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.description import description_meta
        return description_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.description import IDescription
        from adhocracy_core.sheets.description import DescriptionSchema
        from adhocracy_core.sheets import AnnotationStorageSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, AnnotationStorageSheet)
        assert inst.meta.isheet == IDescription
        assert inst.meta.schema_class == DescriptionSchema
        assert inst.meta.editable is True
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'description': ''}


def test_includeme_register_description_sheet(config):
    from adhocracy_core.sheets.description import IDescription
    from adhocracy_core.utils import get_sheet
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.description')
    context = testing.DummyResource(__provides__=IDescription)
    inst = get_sheet(context, IDescription)
    assert inst.meta.isheet is IDescription
