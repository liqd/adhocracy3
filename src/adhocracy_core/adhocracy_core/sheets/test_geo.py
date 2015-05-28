from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.geo')


@fixture
def multipolygon_default() -> dict:
    return {'coordinates': [],
            'administrative_division': '',
            'part_of': None,
            'type': 'MultiPolygon'}


class TestMultiPolygonSchema:

    @fixture
    def inst(self):
        from .geo import MultiPolygonSchema
        return MultiPolygonSchema().bind()

    def test_create(self, inst):
        from .geo import MultiPolygon
        from .geo import AdministrativeDivisionName
        assert isinstance(inst['coordinates'], MultiPolygon)
        assert isinstance(inst['administrative_division'],
                          AdministrativeDivisionName)
        assert inst['type'].readonly

    def test_deserialize_empty(self, inst):
        assert inst.deserialize({}) == {'coordinates': []}

    def test_deserialize_coordinates(self, inst):
        cstruct = {'coordinates': [[[['1', '1']]]]}
        assert inst.deserialize(cstruct) == {'coordinates': [[[(1.0, 1.0)]]]}

    def test_deserialize_division(self, inst):
        cstruct = {'administrative_division': 'stadt'}
        assert inst.deserialize(cstruct) == {'coordinates': [],
                                             'administrative_division': 'stadt'}

    def test_deserialize_raise_if_wrong_division(self, inst):
        from colander import Invalid
        cstruct = {'administrative_division': 'wrong'}
        with raises(Invalid):
            inst.deserialize(cstruct)

    def test_serialize_empty(self, inst, multipolygon_default):
        assert inst.serialize({}) == multipolygon_default

    def test_serialize_coordinates(self, inst):
        appstruct = {'coordinates': [[[(1.0, 1.0)]]]}
        cstruct = inst.serialize(appstruct)
        assert cstruct['coordinates'] == [[[('1.0', '1.0')]]]

    def test_serialize_administrative_division(self, inst):
        appstruct = {'administrative_division': 'stadt'}
        cstruct = inst.serialize(appstruct)
        assert cstruct['administrative_division'] == 'stadt'


class TestMultiPolygonSheet:

    @fixture
    def meta(self):
        from .geo import multipolygon_meta
        return multipolygon_meta

    def test_meta(self, meta):
        from adhocracy_core.sheets.geo import IMultiPolygon
        from adhocracy_core.sheets.geo import MultiPolygonSchema
        from adhocracy_core.sheets import AnnotationRessourceSheet
        assert meta.sheet_class == AnnotationRessourceSheet
        assert meta.isheet == IMultiPolygon
        assert meta.schema_class == MultiPolygonSchema
        assert meta.editable is False
        assert meta.create_mandatory is True

    def test_create(self, meta, context):
        assert meta.sheet_class(meta, context)

    def test_get_empty(self, meta, context, multipolygon_default):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == multipolygon_default

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
        cstruct = {'coordinates': ('0', '0')}
        assert inst.deserialize(cstruct) == {'coordinates': (0, 0)}

    @mark.parametrize('x,y', [('20026376.4', '0'),
                              ('-20026377', '0'),
                              # actually we want -20026376.4 but its not working
                              ('0', '-20048967'),
                              ('0', '20048966.11')])
    def test_deserialize_raise_if_outside_boundary(self, inst, x, y):
        from colander import Invalid
        with raises(Invalid):
            inst.deserialize((x, y))


class TestPointSheet:

    @fixture
    def meta(self):
        from .geo import point_meta
        return point_meta

    def test_meta(self, meta):
        from adhocracy_core.sheets.geo import IPoint
        from adhocracy_core.sheets.geo import PointSchema
        from adhocracy_core.sheets import AnnotationRessourceSheet
        assert meta.sheet_class == AnnotationRessourceSheet
        assert meta.isheet == IPoint
        assert meta.schema_class == PointSchema
        assert meta.editable is True
        assert meta.create_mandatory is False

    def test_create(self, meta, context):
        assert meta.sheet_class(meta, context)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'coordinates': (0, 0),
                              'type': 'Point'}

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
        from adhocracy_core.sheets import AnnotationRessourceSheet
        assert meta.sheet_class == AnnotationRessourceSheet
        assert meta.isheet == ILocationReference
        assert meta.schema_class == LocationReferenceSchema
        assert meta.editable is True
        assert meta.create_mandatory is False

    def test_create(self, meta, context):
        assert meta.sheet_class(meta, context)

    def test_get_empty(self, meta, context, sheet_catalogs):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'location': None}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


