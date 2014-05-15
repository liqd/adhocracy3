"""Simple resource type."""
from substanced.content import add_content_type

from adhocracy.interfaces import ISimple
import adhocracy.sheets.name
from adhocracy.resources import ResourceFactory
from adhocracy.resources.resource import resource_meta_defaults

simple_meta_defaults = \
    resource_meta_defaults._replace(content_name='Simple',
                                    iresource=ISimple,
                                    basic_sheets=[adhocracy.sheets.name.IName,
                                                  ],
                                    )


def includeme(config):
    """Register resource type factory in substanced content registry."""
    metadata = simple_meta_defaults
    identifier = metadata.iresource.__identifier__
    add_content_type(config,
                     identifier,
                     ResourceFactory(metadata),
                     factory_type=identifier, resource_metadata=metadata)
