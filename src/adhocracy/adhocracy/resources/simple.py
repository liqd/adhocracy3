"""Simple resource type."""
from adhocracy.interfaces import ISimple
import adhocracy.sheets.name
import adhocracy.sheets.metadata
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.resource import resource_metadata_defaults


simple_metadata = \
    resource_metadata_defaults._replace(
        iresource=ISimple,
        basic_sheets=[adhocracy.sheets.name.IName,
                      adhocracy.sheets.metadata.IMetadata,
                      ],
    )


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(simple_metadata, config)
