"""Simple resource type."""
from adhocracy.interfaces import ISimple
import adhocracy.sheets.name
from adhocracy.resources.resource import resource_meta_defaults
from adhocracy.resources import add_resource_type_to_registry

simple_meta_defaults = \
    resource_meta_defaults._replace(content_name='Simple',
                                    iresource=ISimple,
                                    basic_sheets=[adhocracy.sheets.name.IName,
                                                  ],
                                    )


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(simple_metadata, config)
