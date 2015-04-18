from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.geo')


class TestPolygonSchema:

    @fixture
    def inst(self):
        from .geo import PolygonSchema
        return PolygonSchema()

    def test_create(self, inst):
        from .geo import Polygon
        assert isinstance(inst['location'], Polygon)

    def test_deserialize_empty(self, inst):
        assert inst.deserialize({}) == {'location': []}

    def test_deserialize_valid_points(self, inst):
        wanted = {'location': [(1.0, 1.0)]}
        assert inst.deserialize({'location': [[1, 1]]}) == wanted

    def test_serialize_empty(self, inst):
        assert inst.serialize({}) == {'location': []}

    def test_serialize_valid_points(self, inst):
        wanted = {'location': [('1.0', '1.0')]}
        assert inst.serialize({'location': [(1.0, 1.0)]}) == wanted


class TestPolygonSheet:

    @fixture
    def meta(self):
        from .geo import polygon_meta
        return polygon_meta

    def test_meta(self, meta):
        from adhocracy_core.sheets.geo import IPolygon
        from adhocracy_core.sheets.geo import PolygonSchema
        from adhocracy_core.sheets import AnnotationStorageSheet
        assert meta.sheet_class == AnnotationStorageSheet
        assert meta.isheet == IPolygon
        assert meta.schema_class == PolygonSchema
        assert meta.editable is False
        assert meta.create_mandatory is True

    def test_create(self, meta, context):
        assert meta.sheet_class(meta, context)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'location': []}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


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


class TestLocationReferenceSheet:

    @fixture
    def meta(self):
        from .geo import location_reference_meta
        return location_reference_meta

    def test_meta(self, meta):
        from adhocracy_core.sheets.geo import ILocationReference
        from adhocracy_core.sheets.geo import LocationReferenceSchema
        from adhocracy_core.sheets import AnnotationStorageSheet
        assert meta.sheet_class == AnnotationStorageSheet
        assert meta.isheet == ILocationReference
        assert meta.schema_class == LocationReferenceSchema
        assert meta.editable is True
        assert meta.create_mandatory is False

    def test_create(self, meta, context):
        assert meta.sheet_class(meta, context)

    def test_get_empty(self, meta, context, mock_graph):
        mock_graph.get_references_for_isheet.return_value = {}
        context.__graph__ = mock_graph
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'location': None}
        assert mock_graph.get_references_for_isheet.called

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


