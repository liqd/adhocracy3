"""Geo location types."""
from pyramid.registry import Registry
import adhocracy_core.sheets.geo
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.interfaces import ISimple
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.simple import simple_meta
from adhocracy_core.resources.service import service_meta


class IMultiPolygon(ISimple):

    """Geo location MultiPolygon.

    Polygons can store a large list of geo location points.
    To allow long term caching it cannot be modified after creation.
    """

    # TODO add cache for ever cache strategy


multipolygon_meta = simple_meta._replace(
    iresource=IMultiPolygon,
    permission_create='create_multipolygon',
    is_implicit_addable=False,
    extended_sheets=[
        adhocracy_core.sheets.geo.IMultiPolygon,
    ],
)


class ILocationsService(IServicePool):

    """The 'locations' ServicePool."""


locations_service_meta = service_meta._replace(
    iresource=ILocationsService,
    content_name='locations',
    element_types=[
        IMultiPolygon,
    ],
)


def add_locations_service(context: IPool, registry: Registry, options: dict):
    """Add `locations` service to context."""
    registry.content.create(ILocationsService.__identifier__, parent=context)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(multipolygon_meta, config)
    add_resource_type_to_registry(locations_service_meta, config)
