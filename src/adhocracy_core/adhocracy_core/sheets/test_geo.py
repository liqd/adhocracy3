from pyramid import testing
from pytest import fixture


class TestPointSchema:

    @fixture
    def inst(self):
        from .geo import PointSchema
        return PointSchema()

    def test_create(self, inst):
        assert inst['x'].validator.max == 20026376.3
        assert inst['x'].validator.min == -20026376.3
        assert inst['y'].validator.max == 20048966.1
        assert inst['y'].validator.min == -20048966.1


class TestPointSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.geo import point_meta
        return point_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.geo import IPoint
        from adhocracy_core.sheets.geo import PointSchema
        from adhocracy_core.sheets import AnnotationStorageSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, AnnotationStorageSheet)
        assert inst.meta.isheet == IPoint
        assert inst.meta.schema_class == PointSchema
        assert inst.meta.editable is True
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'x': 0,
                              'y': 0}


def test_includeme_register_geo_sheet(config):
    from adhocracy_core.sheets.geo import IPoint
    from adhocracy_core.utils import get_sheet
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.geo')
    context = testing.DummyResource(__provides__=IPoint)
    inst = get_sheet(context, IPoint)
    assert inst.meta.isheet is IPoint
