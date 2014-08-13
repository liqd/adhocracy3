"""ItemVersion resource type."""
from pyramid.traversal import find_interface, find_resource

from adhocracy.events import ItemVersionNewVersionAdded
from adhocracy.events import SheetReferencedItemHasNewVersion
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.interfaces import SheetToSheet
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.resource import resource_metadata_defaults
from adhocracy.sheets import tags
from adhocracy.sheets.versions import IVersionable
import adhocracy.sheets.versions
from adhocracy.utils import get_sheet
from adhocracy.utils import find_graph


def notify_new_itemversion_created(context, registry, options):
    """Notify referencing Resources after creating a new ItemVersion.

    Args:
        context (IItemversion): the newly created resource
        registry (pyramid registry):
        option (dict):
            `root_versions`: List with root resources. Will be passed along to
                            resources that reference old versions so they can
                            decide whether they should update themselfes.
            `creator`: User resource that passed to the creation events.

    Returns:
        None

    """
    new_version = context
    root_versions = options.get('root_versions', [])
    creator = options.get('creator', None)
    old_versions = []
    versionable = get_sheet(context, IVersionable)
    follows = versionable.get()['follows']
    for old_version in follows:
        old_versions.append(old_version)
        _notify_itemversion_has_new_version(old_version, new_version, registry,
                                            creator)
        _notify_referencing_resources_about_new_version(old_version,
                                                        new_version,
                                                        root_versions,
                                                        registry,
                                                        creator)

        # Update LAST tag in parent item
        _update_last_tag(context, registry, old_versions)


def _notify_itemversion_has_new_version(old_version, new_version, registry,
                                        creator):
    event = ItemVersionNewVersionAdded(old_version, new_version, registry,
                                       creator)
    registry.notify(event)


def _notify_referencing_resources_about_new_version(old_version,
                                                    new_version,
                                                    root_versions,
                                                    registry,
                                                    creator):
    graph = find_graph(old_version)
    references = graph.get_back_references(old_version,
                                           base_reftype=SheetToSheet)
    for source, isheet, isheet_field, target in references:
        event = SheetReferencedItemHasNewVersion(source,
                                                 isheet,
                                                 isheet_field,
                                                 old_version,
                                                 new_version,
                                                 registry,
                                                 creator,
                                                 root_versions=root_versions)
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


itemversion_metadata = resource_metadata_defaults._replace(
    content_name='ItemVersion',
    iresource=IItemVersion,
    basic_sheets=[adhocracy.sheets.versions.IVersionable,
                  adhocracy.sheets.metadata.IMetadata,
                  ],
    after_creation=[notify_new_itemversion_created] +
    resource_metadata_defaults.after_creation,
    use_autonaming=True,
    autonaming_prefix='VERSION_',
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(itemversion_metadata, config)
