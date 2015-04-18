"""Basic Pool to give the client a endpoint to post specific resource types."""

from adhocracy_core.interfaces import IServicePool
from adhocracy_core.resources.pool import pool_meta
from adhocracy_core.resources import add_resource_type_to_registry
import adhocracy_core.sheets.name
import adhocracy_core.sheets.pool
import adhocracy_core.sheets.metadata


class IBasicService(IServicePool):

    """Basic :term:`service` resource type.

    The resource name is always set to the `content_name`.
    """

# TODO remove IBasicService, use IService instead


service_meta = pool_meta._replace(
    content_name='service',
    iresource=IBasicService,
    basic_sheets=[adhocracy_core.sheets.pool.IPool,
                  adhocracy_core.sheets.metadata.IMetadata,
                  ],
    permission_add='add_service'
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(service_meta, config)
