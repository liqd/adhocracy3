"""Sheets related to geographical information."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta


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


class IPoint(ISheet):

    """Market interface for the point sheet."""


class PointSchema(colander.MappingSchema):

    """A geographical point on the earth.

    `x`: longitude in web mercator
    `y`: latitude in web mercator
    """

    x = WebMercatorLongitude()
    y = WebMercatorLatitude()


point_meta = sheet_meta._replace(isheet=IPoint,
                                 schema_class=PointSchema,
                                 editable=True,
                                 create_mandatory=False,
                                 )


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(point_meta, config.registry)
