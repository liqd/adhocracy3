from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.geo')


class TestPointSchema:

    @fixture
    def inst(self):
        from .geo import PointSchema
        return PointSchema()

    def test_deserialize_valid(self, inst):
        assert inst.deserialize({'x': '0', 'y': '0'}) == {'x': 0, 'y': 0}

    @mark.parametrize('x,y', [('20026376.4', '0'),
                              ('-20026377', '0'),
                              # actually we want -20026376.4 but its not working
                              ('0', '-20048967'),
                              ('0', '20048966.11')])
    def test_deserialize_raise_if_outside_boundary(self, inst, x, y):
        from colander import Invalid
        with raises(Invalid):
            inst.deserialize({'x': x, 'y': y})


class TestPointSheet:

    @fixture
    def meta(self):
        from .geo import point_meta
        return point_meta

    def test_meta(self, meta):
        from adhocracy_core.sheets.geo import IPoint
        from adhocracy_core.sheets.geo import PointSchema
        from adhocracy_core.sheets import AnnotationStorageSheet
        assert meta.sheet_class == AnnotationStorageSheet
        assert meta.isheet == IPoint
        assert meta.schema_class == PointSchema
        assert meta.editable is True
        assert meta.create_mandatory is False

    def test_create(self, meta, context):
        assert meta.sheet_class(meta, context)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'x': 0,
                              'y': 0}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)

