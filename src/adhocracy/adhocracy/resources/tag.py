"""Tag resource type."""
from substanced.content import add_content_type

from adhocracy.interfaces import ITag
from adhocracy.resources.resource import resource_meta_defaults
from adhocracy.resources import ResourceFactory
import adhocracy.sheets.name
import adhocracy.sheets.tags


tag_meta_defaults = \
    resource_meta_defaults._replace(content_name='Tag',
                                    iresource=ITag,
                                    basic_sheets=[adhocracy.sheets.name.IName,
                                                  adhocracy.sheets.tags.ITag,
                                                  ],
                                    )


def includeme(config):
    """Register resource type factory in substanced content registry."""
    metadata = tag_meta_defaults
    identifier = metadata.iresource.__identifier__
    add_content_type(config,
                     identifier,
                     ResourceFactory(metadata),
                     factory_type=identifier, resource_metadata=metadata)
