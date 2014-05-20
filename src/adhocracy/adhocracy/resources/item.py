"""Default item resource."""
from substanced.content import add_content_type

from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItem
from adhocracy.resources import ResourceFactory
from adhocracy.resources.pool import pool_meta_defaults
import adhocracy.sheets.name
import adhocracy.sheets.tags
import adhocracy.sheets.pool
import adhocracy.sheets.versions
from adhocracy.utils import get_resource_interface


def create_initial_content_for_item(context, registry, options):
    """Add first version and the Tags LAST and FIRST."""
    iresource = get_resource_interface(context)
    metadata = registry.content.resources_metadata()[iresource.__identifier__]
    item_type = metadata['metadata'].item_type
    create = registry.content.create
    first_version = create(item_type.__identifier__, parent=context)

    tag_first_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                     [first_version]},
                      'adhocracy.sheets.name.IName': {'name': u'FIRST'}}
    create(ITag.__identifier__, parent=context, appstructs=tag_first_data)
    tag_last_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                    [first_version]},
                     'adhocracy.sheets.name.IName': {'name': u'LAST'}}
    create(ITag.__identifier__, parent=context, appstructs=tag_last_data)


item_meta_defaults = pool_meta_defaults._replace(
    content_name='Item',
    iresource=IItem,
    basic_sheets=[adhocracy.sheets.name.IName,
                  adhocracy.sheets.tags.ITags,
                  adhocracy.sheets.versions.IVersions,
                  adhocracy.sheets.pool.IPool,
                  ],
    element_types=[IItemVersion,
                   ITag,
                   ],
    after_creation=[create_initial_content_for_item],
    item_type=IItemVersion,
)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    metadata = item_meta_defaults
    identifier = metadata.iresource.__identifier__
    add_content_type(config,
                     identifier,
                     ResourceFactory(metadata),
                     factory_type=identifier, resource_metadata=metadata)
