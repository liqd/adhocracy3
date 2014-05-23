"""ItemVersion resource type."""
from pyramid.traversal import find_interface, find_resource
from substanced.content import add_content_type

from adhocracy.events import ItemVersionNewVersionAdded, \
    SheetReferencedItemHasNewVersion
from adhocracy.graph import get_follows, get_back_references
from adhocracy.interfaces import IItemVersion, IItem
from adhocracy.resources.resource import resource_meta_defaults
from adhocracy.resources import ResourceFactory
from adhocracy.sheets import tags
import adhocracy.sheets.versions
from adhocracy.utils import get_sheet


def notify_new_itemversion_created(context, registry, options):
    """Notify referencing Resources after creating a new ItemVersion.

    Args:
        context (IItemversion): the newly created resource
        registry (pyramid registry):
        option (dict): Dict with 'root_versions', a list of
            root resources. Will be passed along to resources that
            reference old versions so they can decide whether they should
            update themselfes.
    Returns:
        None

    """
    new_version = context
    root_versions = options.get('root_versions', [])
    old_versions = []
    for old_version in get_follows(context):
        old_versions.append(old_version)
        _notify_itemversion_has_new_version(old_version, new_version, registry)
        _notify_referencing_resources_about_new_version(old_version,
                                                        new_version,
                                                        root_versions,
                                                        registry)

        # Update LAST tag in parent item
        _update_last_tag(context, registry, old_versions)


def _notify_itemversion_has_new_version(old_version, new_version, registry):
    event = ItemVersionNewVersionAdded(old_version, new_version)
    registry.notify(event)


def _notify_referencing_resources_about_new_version(old_version,
                                                    new_version,
                                                    root_versions,
                                                    registry):
    references = get_back_references(old_version)
    for source, isheet, isheet_field, target in references:
        event = SheetReferencedItemHasNewVersion(source,
                                                 isheet,
                                                 isheet_field,
                                                 old_version,
                                                 new_version,
                                                 root_versions)
        registry.notify(event)


def _update_last_tag(context, registry, old_versions):
    """Update the LAST tag in the parent item of a new version.

    Args:
        context (IResource): the newly created resource
        registry: the registry
        old_versions (list of IItemVersion): list of versions followed by the
                                              new one.

    """
    parent_item = find_interface(context, IItem)
    if parent_item is None:
        return

    tag_sheet = get_sheet(parent_item, tags.ITags)
    taglist = tag_sheet.get_cstruct()['elements']

    for tag in taglist:
        tag_name = tag.split('/')[-1]
        if tag_name == 'LAST':
            tag = find_resource(context, tag)
            sheet = get_sheet(tag, tags.ITag)
            data = sheet.get()
            updated_references = []
            # Remove predecessors, keep the rest
            for reference in data['elements']:
                if reference not in old_versions:
                    updated_references.append(reference)
            # Append new version to end of list
            updated_references.append(context)
            data['elements'] = updated_references
            sheet.set(data)


itemversion_meta_defaults = resource_meta_defaults._replace(
    content_name='ItemVersion',
    iresource=IItemVersion,
    basic_sheets=[adhocracy.sheets.versions.IVersionable,
                  ],
    after_creation=[notify_new_itemversion_created],
    use_autonaming=True,
    autonaming_prefix='VERSION_',
)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    metadata = itemversion_meta_defaults
    identifier = metadata.iresource.__identifier__
    add_content_type(config,
                     identifier,
                     ResourceFactory(metadata),
                     factory_type=identifier, resource_metadata=metadata)
