from pyramid import testing
from pytest import fixture
from pytest import mark


class TestDescriptionSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.description import description_meta
        return description_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.description import IDescription
        from adhocracy_core.sheets.description import DescriptionSchema
        from adhocracy_core.sheets import AnnotationRessourceSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == IDescription
        assert inst.meta.schema_class == DescriptionSchema
        assert inst.meta.editable is True
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'short_description': '',
                              'description': ''
                              }

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, config):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert config.registry.content.get_sheet(context, meta.isheet)
