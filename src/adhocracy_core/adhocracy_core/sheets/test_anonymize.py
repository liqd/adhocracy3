from pyramid import testing
from pytest import fixture
from pytest import mark


class TestAllowAddAnonymizedSheet:

    @fixture
    def meta(self):
        from .anonymize import allow_add_anonymized_meta
        return allow_add_anonymized_meta

    def test_meta(self, meta):
        from . import anonymize
        assert meta.isheet == anonymize.IAllowAddAnonymized
        assert meta.schema_class == anonymize.AllowAddAnonymizedSchema
        assert meta.editable is False
        assert meta.creatable is False

    def test_create(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {}

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)
