"""Tag resource type."""
from adhocracy.interfaces import ITag
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.resource import resource_metadata_defaults
import adhocracy.sheets.name
import adhocracy.sheets.tags
import adhocracy.sheets.metadata


tag_metadata = resource_metadata_defaults._replace(
    iresource=ITag,
    basic_sheets=[adhocracy.sheets.name.IName,
                  adhocracy.sheets.metadata.IMetadata,
                  adhocracy.sheets.tags.ITag,
                  ],
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(tag_metadata, config)
