"""Resource type configuration and default factory."""
from adhocracy.events import ItemNewVersionAdded
from adhocracy.events import SheetReferencedItemHasNewVersion
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import AdhocracyReferenceType
from adhocracy.utils import get_all_taggedvalues
from adhocracy.utils import get_resource_interface
from adhocracy.sheets.versions import IVersionableFollowsReference
from pyramid.path import DottedNameResolver
from pyramid.threadlocal import get_current_registry
from substanced.util import get_oid
from substanced.objectmap import find_objectmap
from zope.component import getMultiAdapter
from zope.interface import directlyProvides
from zope.interface import alsoProvides

import datetime


def item_create_initial_content(context, registry, options):
    """Add first version and the Tags LAST and FIRST."""
    iface = get_resource_interface(context)
    item_type = get_all_taggedvalues(iface)['item_type']
    first_version = ResourceFactory(item_type)(context)

    first_version_oid = get_oid(first_version)
    tag_first_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                     [first_version_oid]},
                      'adhocracy.sheets.name.IName': {'name': u'FIRST'}}
    ResourceFactory(ITag)(context, appstructs=tag_first_data)

    tag_last_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                    [first_version_oid]},
                     'adhocracy.sheets.name.IName': {'name': u'LAST'}}
    ResourceFactory(ITag)(context, appstructs=tag_last_data)


def itemversion_create_notify(context, registry, options):
    """Notify referencing Items after creating a new ItemVersion.

    Args:
        context (IResource): the newly created resource
        registry: the substanced registry
        option (dict): Dict with 'root_versions', a list of
            root resources. Will be passed along to resources that
            reference old versions so they can decide whether they should
            update themselfes.

    """
    om = find_objectmap(context)
    if registry is not None and om is not None:
        follows = list(om.targets(context, IVersionableFollowsReference))
        new_version = context
        new_version_oid = get_oid(new_version)

        # Convert resource paths to resources

        # FIXME make sure options alread contains a list of validated
        # resources. Validation should happen in views.
        root_versions = options.get('root_versions', [])

        for old_version in follows:
            old_version_oid = get_oid(old_version)
            # Notify that an new ItemVersion is being created
            event_new = ItemNewVersionAdded(new_version.__parent__,
                                            old_version,
                                            new_version)
            registry.notify(event_new)
            # Notify all items that reference the old ItemVersion
            for reftype in om.get_reftypes():
                if not issubclass(reftype, AdhocracyReferenceType):
                    # we do not care for standard substanced reference types
                    continue
                for other in om.sources(old_version, reftype):
                    event_ref = SheetReferencedItemHasNewVersion(
                        other,
                        reftype.getTaggedValue('source_isheet'),
                        reftype.getTaggedValue('source_isheet_field'),
                        old_version_oid,
                        new_version_oid,
                        root_versions
                    )
                    registry.notify(event_ref)


class ResourceFactory(object):

    """Basic resource factory."""

    def __init__(self, iface):
        res = DottedNameResolver()
        iface = res.maybe_resolve(iface)
        assert iface.isOrExtends(IResource)
        meta = get_all_taggedvalues(iface)
        self.resource_iface = iface
        self.class_ = meta['content_class']
        self.prop_ifaces = []
        for prop_iface in meta['basic_sheets'].union(meta['extended_sheets']):
            assert prop_iface.isOrExtends(ISheet)
            self.prop_ifaces.append(prop_iface)
        self.after_creation = meta['after_creation']

    def add(self, context, resource, appstructs):
        """Add to context.

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
            name = context.check_name(name)
            appstructs[name_identifier]['name'] = name
        if not name:
            name = datetime.datetime.now().isoformat()
        if IItemVersion.providedBy(resource):
            name = context.next_name(resource, prefix='VERSION_')
        context.add(name, resource, send_events=False)

    def __call__(self,
                 context,
                 appstructs={},
                 run_after_creation=True,
                 add_to_context=True,
                 **kwargs
                 ):
        """Triggered whan a ResourceFactory instance is called.

        Args:
            context (IResource):
            add_to_context (bool): make context the parent of the new resource.
                Default is True.
            after_creation (bool): whether to invoke after_creation hooks
                Default is True.
            appstructs (dict): key/values of sheet appstruct data. Key is an
                identifier of a sheet interface. Value is the data to set.
            **kwargs: arbitary keyword arguments. Will be passed along to
                after_creation hooks as 3rd argument 'options'.

        Returns:
            object (IResource): the newly created resource

        """
        res = DottedNameResolver()
        resource = self.class_()
        directlyProvides(resource, self.resource_iface)
        alsoProvides(resource, self.prop_ifaces)

        if add_to_context:
            self.add(context, resource, appstructs)
        else:
            resource.__parent__ = None
            resource.__name__ = ''

        if appstructs:
            for key, struct in appstructs.items():
                iface = res.maybe_resolve(key)
                sheet = getMultiAdapter((resource, iface),
                                        IResourcePropertySheet)
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
