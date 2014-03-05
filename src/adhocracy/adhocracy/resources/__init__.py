"""Resource type configuration and default factory."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import ITag
from adhocracy.interfaces import IItemVersion
from adhocracy.utils import get_all_taggedvalues
from adhocracy.utils import get_resource_interface
from pyramid.path import DottedNameResolver
from substanced.util import get_oid
from zope.component import getMultiAdapter
from zope.interface import directlyProvides
from zope.interface import alsoProvides

import datetime


def item_create_initial_content(context, registry):
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


class ResourceFactory(object):

    """Basic resource factory."""

    def __init__(self, iface):
        res = DottedNameResolver()
        iface = res.maybe_resolve(iface)
        assert iface.isOrExtends(IResource)
        meta = get_all_taggedvalues(iface)
        self.resource_iface = iface
        self.class_ = res.maybe_resolve(meta['content_class'])
        self.prop_ifaces = []
        for i in meta['basic_sheets'].union(meta['extended_sheets']):
            prop_iface = res.maybe_resolve(i)
            assert prop_iface.isOrExtends(ISheet)
            self.prop_ifaces.append(prop_iface)
        self.after_creation = [res.maybe_resolve(call) for call in
                               meta['after_creation']]

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
                 add_to_context=True
                 ):
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
            for call in self.after_creation:
                call(resource, None)
        return resource


def includeme(config):
    """Include all resource types in this package."""
    config.include('.pool')
    config.include('.tag')
    config.include('.section')
    config.include('.proposal')
