"""Pool resource type."""
from substanced.content import add_content_type

import adhocracy.sheets.name
import adhocracy.sheets.pool
from adhocracy.folder import ResourcesAutolNamingFolder
from adhocracy.interfaces import IPool
from adhocracy.resources import resource_meta_defaults
from adhocracy.resources import ResourceFactory


class IBasicPool(IPool):

    """Basic Pool."""

pool_meta_defaults = resource_meta_defaults._replace(
    content_name=IBasicPool.__identifier__,
    iresource=IBasicPool,
    content_class=ResourcesAutolNamingFolder,
    basic_sheets=[adhocracy.sheets.name.IName,
                  adhocracy.sheets.pool.IPool,
                  ],
    element_types=[IPool],
)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    metadata = pool_meta_defaults
    identifier = metadata.iresource.__identifier__
    add_content_type(config,
                     identifier,
                     ResourceFactory(metadata),
                     factory_type=identifier, resource_metadata=metadata)
