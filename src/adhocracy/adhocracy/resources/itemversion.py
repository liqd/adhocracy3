"""ItemVersion resource type."""
from substanced.content import add_content_type

from adhocracy.interfaces import IItemVersion
from adhocracy.resources import resource_meta_defaults
from adhocracy.resources import ResourceFactory
from adhocracy.resources import notify_new_itemversion_created
import adhocracy.sheets.versions


itemversion_meta_defaults = resource_meta_defaults._replace(
    content_name='ItemVersion',
    iresource=IItemVersion,
    basic_sheets=[adhocracy.sheets.versions.IVersionable,
                  ],
    after_creation=[notify_new_itemversion_created],
)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    metadata = itemversion_meta_defaults
    identifier = metadata.iresource.__identifier__
    add_content_type(config,
                     identifier,
                     ResourceFactory(metadata),
                     factory_type=identifier, resource_metadata=metadata)
