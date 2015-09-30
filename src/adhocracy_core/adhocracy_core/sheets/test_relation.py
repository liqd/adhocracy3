from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark

@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets.relation')


class TestPolarizableSheet:

    @fixture
    def inst(self, pool, service):
        pool['relations'] = service
        from adhocracy_core.sheets.relation import polarizable_meta
        return polarizable_meta.sheet_class(polarizable_meta, pool)

    def test_create(self, inst):
        from adhocracy_core.sheets import AnnotationRessourceSheet
        from adhocracy_core.sheets.relation import IPolarizable
        from adhocracy_core.sheets.relation import PolarizableSchema
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == IPolarizable
        assert inst.meta.schema_class == PolarizableSchema
        assert inst.meta.editable is True
        assert inst.meta.creatable is True
        assert inst.meta.create_mandatory is True


    def test_get_empty(self, inst):
        post_pool = inst.context['relations']
        assert inst.get() == {'post_pool': post_pool,
                              'polarizations': []}

class TestPolarizationSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.relation import polarization_meta
        return polarization_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.relation import IPolarization
        from adhocracy_core.sheets.relation import PolarizationSchema
        from adhocracy_core.sheets import AnnotationRessourceSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == IPolarization
        assert inst.meta.schema_class == PolarizationSchema
        assert inst.meta.create_mandatory

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'subject': None,
                              'object': None,
                              'position': 'pro',
                              }
