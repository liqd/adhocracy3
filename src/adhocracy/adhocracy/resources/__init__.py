"""Resource type configuration and default factory."""
from adhocracy.events import ItemVersionNewVersionAdded
from adhocracy.events import SheetReferencedItemHasNewVersion
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItemVersion
from adhocracy.utils import get_all_taggedvalues
from adhocracy.utils import get_resource_interface
from adhocracy.utils import get_reftypes
from adhocracy.sheets.versions import IVersionableFollowsReference
from pyramid.path import DottedNameResolver
from pyramid.threadlocal import get_current_registry
from substanced.util import get_oid
from substanced.objectmap import find_objectmap
from zope.interface import directlyProvides
from zope.interface import alsoProvides

import datetime


def create_initial_content_for_item(context, registry, options):
    """Add first version and the Tags LAST and FIRST."""
    iface = get_resource_interface(context)
    item_type = get_all_taggedvalues(iface)['item_type']
    first_version = ResourceFactory(item_type)(parent=context)

    first_version_oid = get_oid(first_version)
    tag_first_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                     [first_version_oid]},
                      'adhocracy.sheets.name.IName': {'name': u'FIRST'}}
    ResourceFactory(ITag)(parent=context, appstructs=tag_first_data)

    tag_last_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                    [first_version_oid]},
                     'adhocracy.sheets.name.IName': {'name': u'LAST'}}
    ResourceFactory(ITag)(parent=context, appstructs=tag_last_data)


def _get_old_versions(context):
    #FIXME extend graph or versions sheet for this helper
    om = find_objectmap(context)
    old_versions = iter([])
    if om:
        old_versions = om.targets(context, IVersionableFollowsReference)
    return old_versions


def _notify_itemversion_has_new_version(old_version, new_version, registry):
    event = ItemVersionNewVersionAdded(old_version, new_version)
    registry.notify(event)


def _notify_referencing_resources_about_new_version(old_version,
                                                    new_version,
                                                    root_versions,
                                                    registry):
    om = find_objectmap(old_version)
    reftypes = get_reftypes(om, [IVersionableFollowsReference])
    for reftype in reftypes:
        for referencing in om.sources(old_version, reftype):
            event = SheetReferencedItemHasNewVersion(
                referencing,
                reftype.getTaggedValue('source_isheet'),
                reftype.getTaggedValue('source_isheet_field'),
                old_version.__oid__,
                new_version.__oid__,
                root_versions)
            registry.notify(event)


def notify_new_itemversion_created(context, registry, options):
    """Notify referencing Resources after creating a new ItemVersion.

    Args:
        context (IItemversion): the newly created resource
        registry (pyramid registry or None): None is allowed to ease testing.
        option (dict): Dict with 'root_versions', a list of
            root resources. Will be passed along to resources that
            reference old versions so they can decide whether they should
            update themselfes.
    Returns:
        None

    """
    if registry is None:
        return None
    new_version = context
    root_versions = options.get('root_versions', [])
    old_versions = _get_old_versions(context)
    for old_version in old_versions:
        _notify_itemversion_has_new_version(old_version, new_version, registry)
        _notify_referencing_resources_about_new_version(old_version,
                                                        new_version,
                                                        root_versions,
                                                        registry)


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
    config.include('.pool')
    config.include('.tag')
    config.include('.paragraph')
    config.include('.section')
    config.include('.proposal')
