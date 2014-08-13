"""Default item resource."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItem
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.pool import pool_metadata
import adhocracy.sheets.name
import adhocracy.sheets.tags
import adhocracy.sheets.pool
import adhocracy.sheets.versions
from adhocracy.utils import get_iresource


def create_initial_content_for_item(context, registry, options):
    """Add first version and the Tags LAST and FIRST."""
    iresource = get_iresource(context)
    metadata = registry.content.resources_meta[iresource.__identifier__]
    item_type = metadata.item_type
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


item_metadata = pool_metadata._replace(
    content_name='Item',
    iresource=IItem,
    basic_sheets=[adhocracy.sheets.name.IName,
                  adhocracy.sheets.tags.ITags,
                  adhocracy.sheets.versions.IVersions,
                  adhocracy.sheets.pool.IPool,
                  adhocracy.sheets.metadata.IMetadata,
                  ],
    element_types=[IItemVersion,
                   ITag,
                   ],
    after_creation=[create_initial_content_for_item] +
    pool_metadata.after_creation,
    item_type=IItemVersion,
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(item_metadata, config)
