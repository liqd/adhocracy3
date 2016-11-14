"""'Activity stream resource type."""
from pyramid.registry import Registry

from adhocracy_core.interfaces import ISimple
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.simple import simple_meta
from adhocracy_core.resources.service import service_meta
import adhocracy_core.sheets.activity
import adhocracy_core.sheets.metadata


class IActivity(ISimple):
    """An activity stream entry."""

activity_meta = simple_meta._replace(
    content_name='Activity',
    iresource=IActivity,
    permission_create='create_activity',
    autonaming_prefix='activity',
    basic_sheets=(adhocracy_core.sheets.metadata.IMetadata,
                  adhocracy_core.sheets.activity.IActivity,
                  ),
)


class IActivityService(IServicePool):
    """The 'activity' ServicePool."""


activity_service_meta = service_meta._replace(
    iresource=IActivityService,
    content_name='activity_stream',
    element_types=(IActivity,),
)


def add_activiy_service(context: IPool, registry: Registry, options: dict):
    """Add `activity` service to context."""
    registry.content.create(IActivityService.__identifier__,
                            parent=context,
                            autoupdated=True)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(activity_meta, config)
    add_resource_type_to_registry(activity_service_meta, config)
