"""Resource type configuration and default factory."""
import datetime

from pyramid.traversal import find_interface
from pyramid.path import DottedNameResolver
from pyramid.threadlocal import get_current_registry
from pyramid.registry import Registry
from substanced.util import get_oid
from substanced.content import add_content_type
from substanced.objectmap import find_objectmap
from zope.interface import directlyProvides
from zope.interface import alsoProvides

from adhocracy.events import ItemVersionNewVersionAdded
from adhocracy.events import SheetReferencedItemHasNewVersion
from adhocracy.graph import get_back_references
from adhocracy.graph import get_references_for_isheet
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItem
from adhocracy.interfaces import IItemVersion
from adhocracy.utils import get_all_taggedvalues
from adhocracy.utils import get_resource_interface
from adhocracy.utils import get_sheet
from adhocracy.sheets import tags
from adhocracy.sheets.versions import IVersionable


def add_resource_type_to_registry(iresource: IResource, config: Registry):
    """Add the `iresource` type to the content registry.

    As generic factory the :class:`ResourceFactory` is used.
    """
    assert hasattr(config.registry, 'content')
    name = iresource.queryTaggedValue('content_name')
    if not name:
        name = iresource.__identifier__
    meta = {'content_name': name,
            'add_view': 'add_' + iresource.__identifier__,
            }
    add_content_type(config, iresource.__identifier__,
                     ResourceFactory(iresource),
                     factory_type=iresource.__identifier__, **meta)


def create_initial_content_for_item(context, registry, options):
    """Add first version and the Tags LAST and FIRST."""
    iface = get_resource_interface(context)
    item_type = get_all_taggedvalues(iface)['item_type']
    first_version = ResourceFactory(item_type)(parent=context)

    first_version_oid = first_version.__oid__
    tag_first_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                     [first_version_oid]},
                      'adhocracy.sheets.name.IName': {'name': u'FIRST'}}
    ResourceFactory(ITag)(parent=context, appstructs=tag_first_data)

    tag_last_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                    [first_version_oid]},
                     'adhocracy.sheets.name.IName': {'name': u'LAST'}}
    ResourceFactory(ITag)(parent=context, appstructs=tag_last_data)


def _update_last_tag(context, registry, old_version_oids):
    """Update the LAST tag in the parent item of a new version.

    Args:
        context (IResource): the newly created resource
        registry: the registry
        old_version_oids (list of int): list of versions followed by the new
            one

    """
    parent_item = find_interface(context, IItem)
    if parent_item is None:
        return

    om = find_objectmap(context)
    tag_sheet = get_sheet(parent_item, tags.ITags)
    taglist = tag_sheet.get_cstruct()['elements']

    if taglist:
        for tag in taglist:
            # find LAST tag (last part of tag name must be 'LAST')
            if tag.split('/')[-1] == ('LAST'):
                last_tag = om.object_for((tag,))
                if last_tag is not None:
                    itag_sheet = get_sheet(last_tag, tags.ITag)
                    itag_dict = itag_sheet.get()
                    oids_before = itag_dict['elements']
                    oids_after = []

                    # Remove OIDs of our predecessors, keep the rest
                    for oid in oids_before:
                        if oid not in old_version_oids:
                            oids_after.append(oid)

                    # Append OID of new version to end of list
                    oids_after.append(context.__oid__)
                    itag_dict['elements'] = oids_after
                    itag_sheet.set(itag_dict)


def _get_old_versions(context):
    versions = get_references_for_isheet(context, IVersionable)
    return versions.get('follows', [])


def _notify_itemversion_has_new_version(old_version, new_version, registry):
    event = ItemVersionNewVersionAdded(old_version, new_version)
    registry.notify(event)


def _notify_referencing_resources_about_new_version(old_version,
                                                    new_version,
                                                    root_versions,
                                                    registry):
    references = get_back_references(old_version)
    for referencing, isheet, isheet_field in references:
        event = SheetReferencedItemHasNewVersion(referencing,
                                                 isheet,
                                                 isheet_field,
                                                 old_version.__oid__,
                                                 new_version.__oid__,
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
    old_version_oids = []
    for old_version in _get_old_versions(context):
        old_version_oids.append(get_oid(old_version))
        _notify_itemversion_has_new_version(old_version, new_version, registry)
        _notify_referencing_resources_about_new_version(old_version,
                                                        new_version,
                                                        root_versions,
                                                        registry)

        # Update LAST tag in parent item
        _update_last_tag(context, registry, old_version_oids)


class ResourceFactory(object):

    """Basic resource factory."""

    def __init__(self, iresource):
        iresource = DottedNameResolver().maybe_resolve(iresource)
        assert iresource.isOrExtends(IResource)
        self.iresource = iresource
        meta = get_all_taggedvalues(iresource)
        self.class_ = meta['content_class']
        isheets = meta['basic_sheets'].union(meta['extended_sheets'])
        for isheet in isheets:
            assert isheet.isOrExtends(ISheet)
        self.isheets = isheets
        self.after_creation = meta['after_creation']

    def _add(self, parent, resource, appstructs):
        """Add resource to context folder.

        Returns:
            name (String)
        Raises:
            substanced.folder.FolderKeyError
            ValueError

        """
        # TODO use seperated factory for IVersionables
        name_identifier = 'adhocracy.sheets.name.IName'
        name = ''
        if name_identifier in appstructs:
            name = appstructs[name_identifier]['name']
            name = parent.check_name(name)
            appstructs[name_identifier]['name'] = name
        if not name:
            name = datetime.datetime.now().isoformat()
        if IItemVersion.providedBy(resource):
            name = parent.next_name(resource, prefix='VERSION_')
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
        resource = self.class_()
        directlyProvides(resource, self.iresource)
        alsoProvides(resource, self.isheets)

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
            for call in self.after_creation:
                call(resource, registry, options=kwargs)

        return resource


def includeme(config):
    """Include all resource types in this package."""
    # config.include('.pool')
    # config.include('.tag')
