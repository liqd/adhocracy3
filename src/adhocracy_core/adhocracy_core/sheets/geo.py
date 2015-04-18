"""Sheets related to geographical information."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import Reference


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

    x = WebMercatorLongitude()
    y = WebMercatorLatitude()


class Polygon(colander.SequenceSchema):

    """List of geographical point on the earth."""

    point = Point()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'default' not in kwargs:  # pragma: no branch
            self.default = []
            self.missing = []


class IPolygon(ISheet):

    """Market interface for the polygon sheet."""


class PolygonSchema(colander.MappingSchema):

    """A geographical polygon on the earth."""

    location = Polygon()


polygon_meta = sheet_meta._replace(isheet=IPolygon,
                                   schema_class=PolygonSchema,
                                   editable=False,
                                   create_mandatory=True,
                                   )


class ILocationReference(ISheet):

    """Marker interface for the location reference sheet."""


class LocationReference(SheetToSheet):

    """Reference to a geo location."""

    source_isheet = ILocationReference
    target_isheet = IPolygon


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

    """A geographical point on the earth.

    `x`: longitude in web mercator
    `y`: latitude in web mercator
    """

    x = WebMercatorLongitude()
    y = WebMercatorLatitude()

# FIXME use Point tuple instead, for example: location = Point()

point_meta = sheet_meta._replace(isheet=IPoint,
                                 schema_class=PointSchema,
                                 editable=True,
                                 create_mandatory=False,
                                 )


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(point_meta, config.registry)
    add_sheet_to_registry(polygon_meta, config.registry)
    add_sheet_to_registry(location_reference_meta, config.registry)
