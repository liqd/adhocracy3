"""Resource type configuration and default factory."""
import datetime

from pyramid.traversal import find_interface
from pyramid.traversal import find_resource
from pyramid.path import DottedNameResolver
from pyramid.threadlocal import get_current_registry
from zope.interface import directlyProvides
from zope.interface import alsoProvides

from adhocracy.events import ItemVersionNewVersionAdded
from adhocracy.events import SheetReferencedItemHasNewVersion
from adhocracy.graph import get_back_references
from adhocracy.graph import get_follows
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItem
from adhocracy.interfaces import ResourceMetadata
from adhocracy.utils import get_resource_interface
from adhocracy.utils import get_sheet
from adhocracy.sheets import tags


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


class ResourceFactory:

    """Basic resource factory."""

    name_identifier = 'adhocracy.sheets.name.IName'

    def __init__(self, metadata: ResourceMetadata):
        self.meta = metadata

    def _add(self, parent, resource, appstructs):
        """Add resource to context folder.

        Returns:
            name (String)
        Raises:
            substanced.folder.FolderKeyError
            ValueError

        """
        # TODO use seperated factory for IVersionables
        name = ''
        if self.name_identifier in appstructs:
            name = appstructs[self.name_identifier]['name']
            name = parent.check_name(name)
            appstructs[self.name_identifier]['name'] = name
        if not name:
            name = datetime.datetime.now().isoformat()
        if self.meta.use_autonaming:
            prefix = self.meta.autonaming_prefix
            name = parent.next_name(resource, prefix=prefix)
        parent.add(name, resource, send_events=False)

    def __call__(self,
                 parent=None,
                 appstructs={},
                 run_after_creation=True,
                 **kwargs
                 ):
        """Triggered whan a ResourceFactory instance is called.

        Args:
            parent (IPool or None): Add the new resource to this pool.
                                    None value is allowed to create non
                                    persistent Resources (without OID/parent).
            appstructs (dict): Key/Values of sheet appstruct data.
                               Key is anidentifier of a sheet interface.
                               Value is the data to set.
            after_creation (bool): Whether to invoke after_creation hooks,
                                   Default is True.
                                   If parent is None you should set this False
            **kwargs: Arbitary keyword arguments. Will be passed along to
                after_creation hooks as 3rd argument 'options'.

        Returns:
            object (IResource): the newly created resource

        """
        resource = self.meta.content_class()
        directlyProvides(resource, self.meta.iresource)
        isheets = self.meta.basic_sheets + self.meta.extended_sheets
        alsoProvides(resource, isheets)

        if parent is not None:
            self._add(parent, resource, appstructs)
        else:
            resource.__parent__ = None
            resource.__name__ = ''

        if appstructs:
            for key, struct in appstructs.items():
                iface = DottedNameResolver().maybe_resolve(key)
                sheet = get_sheet(resource, iface)
                if not sheet.readonly:
                    sheet.set(struct)

        if run_after_creation:
            registry = get_current_registry()
            for call in self.meta.after_creation:
                call(resource, registry, options=kwargs)

        return resource


def includeme(config):
    """Include all resource types in this package."""
    config.include('.pool')
    config.include('.tag')
    config.include('.itemversion')
    config.include('.item')
