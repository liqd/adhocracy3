from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark

@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets.polarization')

class TestPolarizableSheet:

    @fixture
    def inst(self, pool, service):
        from adhocracy_core.sheets.polarization import polarizable_meta
        return polarizable_meta.sheet_class(polarizable_meta, pool)

    def test_create(self, inst):
        from adhocracy_core.sheets import AnnotationRessourceSheet
        from adhocracy_core.sheets.polarization import IPolarizable
        from adhocracy_core.sheets.polarization import PolarizableSchema
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == IPolarizable
        assert inst.meta.schema_class == PolarizableSchema
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, inst):
        assert inst.get() == {'position': 'pro'}
