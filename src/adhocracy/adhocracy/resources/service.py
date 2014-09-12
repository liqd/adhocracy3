"""Pool resource type and zodb persistent IPool implementation."""

import adhocracy.sheets.name
import adhocracy.sheets.pool
import adhocracy.sheets.metadata
from adhocracy.interfaces import IServicePool
from adhocracy.resources.pool import pool_metadata
from adhocracy.resources import add_resource_type_to_registry


class IBasicService(IServicePool):

    """Basic :term:`service` resource type.

    The resource name is always set to the `content_name`.
    """


service_metadata = pool_metadata._replace(
    content_name='Service',
    iresource=IBasicService,
    basic_sheets=[adhocracy.sheets.pool.IPool,
                  adhocracy.sheets.metadata.IMetadata,
                  ],
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(service_metadata, config)
