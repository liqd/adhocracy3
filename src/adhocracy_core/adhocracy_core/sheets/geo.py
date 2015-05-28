"""Sheets related to geographical information."""
from enum import Enum
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import Reference
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import AdhocracySequenceNode


class WebMercatorLongitude(colander.SchemaNode):

    """A a web mercator longitude value.

    Validation values taken from http://epsg.io/3857.
    """

    schema_type = colander.Float
    default = 0
    missing = colander.drop
    validator = colander.Range(min=-20026376.3, max=20026376.3)


class WebMercatorLatitude(colander.SchemaNode):

    """A a web mercator latitude value.

    Validation values taken from http://epsg.io/3857.
    """

    schema_type = colander.Float
    default = 0
    missing = colander.drop
    validator = colander.Range(min=-20048966.10, max=20048966.10)


class Point(colander.TupleSchema):

    """A geographical point on the earth.

    `x`: longitude in web mercator
    `y`: latitude in web mercator
    """

    default = (0, 0)
    missing = colander.drop

    x = WebMercatorLongitude()
    y = WebMercatorLatitude()


class LineString(AdhocracySequenceNode):

    """List of geographical points on the earth."""

    missing = []

    point = Point()


class Polygon(AdhocracySequenceNode):

    """List of geographical lines on the earth."""

    missing = []

    line = LineString()


class MultiPolygon(AdhocracySequenceNode):

    """List of geographical polygons on the earth."""

    missing = []

    polygon = Polygon()


class IMultiPolygon(ISheet):

    """Market interface for the multi polygon sheet."""


class PartOfReference(SheetToSheet):

    """Reference to a geographical object."""

    source_isheet = IMultiPolygon
    source_isheet_field = 'part_of'
    target_isheet = IMultiPolygon


class GermanAdministrativeDivisions(Enum):

    """Administrative division names/levels based on the wikidata ontology."""

    staat = 2
    bundesland = 4
    regierungsbezirk = 5
    kreis = 6
    landkreis = 6
    gemeinde = 8
    stadt = 8
    stadtbezirk = 9
    ortsteil = 10
    bezirksregion = 10
    """Custom definition. Is part of stadtbezirk but not part of ortsteil."""


class AdministrativeDivisionName(SingleLine):

    """Administrative division, see :class`GermanAdministrativeDivisions`."""

    def validator(self, node, cstruct):
        division_names = GermanAdministrativeDivisions.__members__.keys()
        return colander.OneOf(division_names)(node, cstruct)


class MultiPolygonSchema(colander.MappingSchema):

    """A geographical MultiPolygon object.

    GeoJSON like geometry object fields:

    `type`: 'MultiPolygon' (geometry object type)
    `coordinates`: list of list of list of points with (longitude, latitude).

    Metadata property fields:

    `administrative_level`: administrative division level
    `administrative_division`: administrative division name
    `part_of`: surrounding geographical object
    """

    type = SingleLine(default='MultiPolygon', readonly=True)
    coordinates = MultiPolygon()

    administrative_division = AdministrativeDivisionName()
    part_of = Reference(reftype=PartOfReference)


multipolygon_meta = sheet_meta._replace(isheet=IMultiPolygon,
                                        schema_class=MultiPolygonSchema,
                                        editable=False,
                                        create_mandatory=True,
                                        )


class ILocationReference(ISheet):

    """Marker interface for the location reference sheet."""


class LocationReference(SheetToSheet):

    """Reference to a geographical object."""

    source_isheet = ILocationReference
    source_isheet_field = 'location'
    target_isheet = IMultiPolygon


class LocationReferenceSchema(colander.MappingSchema):

    """Data structure for the location reference sheet."""

    location = Reference(reftype=LocationReference)


location_reference_meta = sheet_meta._replace(
    isheet=ILocationReference,
    schema_class=LocationReferenceSchema,
)


class IPoint(ISheet):

    """Market interface for the point sheet."""


class PointSchema(colander.MappingSchema):

    """A geographical Point object.

    GeoJSON like geometry object fields:

    `type`: 'Point' (geometry object type)
    `coordinates`: tuple of points with (longitude, latitude).
    """

    type = SingleLine(default='Point', readonly=True)
    coordinates = Point()


point_meta = sheet_meta._replace(isheet=IPoint,
                                 schema_class=PointSchema,
                                 editable=True,
                                 create_mandatory=False,
                                 )


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(point_meta, config.registry)
    add_sheet_to_registry(multipolygon_meta, config.registry)
    add_sheet_to_registry(location_reference_meta, config.registry)
