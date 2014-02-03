"""Resource type configuration and default factory."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.utils import get_ifaces_from_module
from adhocracy.utils import get_all_taggedvalues
from adhocracy.utils import get_resource_interface
from pyramid.path import DottedNameResolver
from substanced.content import add_content_type
from substanced.interfaces import IAutoNamingFolder
from substanced.util import get_oid
from zope.component import getMultiAdapter
from zope.interface import directlyProvides
from zope.interface import alsoProvides
from zope.interface import taggedValue

import sys
import datetime


class IPool(IResource, IAutoNamingFolder):

    """Folder in the object hierarchy.

    Namespace, structure and configure Fubels for a Participation Process.
    Additional TaggedValue: 'addable_content_interfaces'

    """

    taggedValue('content_class', 'adhocracy.folder.ResourcesAutolNamingFolder')
    taggedValue('basic_sheets',
                set(['adhocracy.sheets.name.IName',
                     'adhocracy.sheets.pool.IPool']))
    taggedValue('addable_content_interfaces',
                set(['adhocracy.resources.IPool']))
    """ Set addable content types, class heritage is honored"""


def fubelversionspool_create_initial_content(context, registry):
    """Add first version and the Tags LAST and FIRST."""
    iface = get_resource_interface(context)
    fubel_type = get_all_taggedvalues(iface)['fubel_type']
    fubel_first = ResourceFactory(fubel_type)(context)

    fubel_oid = get_oid(fubel_first)
    tag_first_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                     [fubel_oid]},
                      'adhocracy.sheets.name.IName': {'name': u'FIRST'}}
    ResourceFactory(ITag)(context, appstructs=tag_first_data)

    tag_last_data = {'adhocracy.sheets.tags.ITag': {'elements':
                                                    [fubel_oid]},
                     'adhocracy.sheets.name.IName': {'name': u'LAST'}}
    ResourceFactory(ITag)(context, appstructs=tag_last_data)


class IFubelVersionsPool(IPool):

    """Pool for all VersionableFubels (DAG), tags and related Pools.

    Additional TaggedValue: 'fubel_type'

    """

    taggedValue('content_name', 'FubelVersionsPool')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.IName',
                 'adhocracy.sheets.tags.ITags',
                 'adhocracy.sheets.versions.IVersions',
                 'adhocracy.sheets.pool.IPool']))
    taggedValue('addable_content_interfaces', set([
                'adhocracy.resources.IVersionableFubel',
                'adhocracy.resources.ITag',
                ]))
    taggedValue('after_creation', [fubelversionspool_create_initial_content])
    taggedValue('fubel_type',
                'adhocracy.resources.IVersionableFubel')
    """Type of VersionableFubel for this VersionPool.
    Subtypes have to override.
    """


class IFubel(IResource):

    """Small object without versions and children."""

    taggedValue('content_name', 'Fubel')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.IName']))


class ITag(IResource):

    """Tag to link specific versions."""

    taggedValue('content_name', 'Fubel')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.IName',
                 'adhocracy.sheets.tags.ITag']))


class IVersionableFubel(IResource):

    """Versionable object, created during a Participation Process (mainly)."""

    taggedValue('content_name', 'VersionableFubel')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.versions.IVersionable']))


# Concrete Fubels and FubelVersionsPools

class IProposal(IVersionableFubel):

    """Versionable Fubel with Document propertysheet."""

    taggedValue('extended_sheets', set(
                ['adhocracy.sheets.document.IDocument']))


class IProposalVersionsPool(IFubelVersionsPool):

    """Proposal Versions Pool."""

    taggedValue('addable_content_interfaces', set(
        ['adhocracy.resources.ITag',
         'adhocracy.resources.IFubelVersionsPool',
         'adhocracy.resources.IProposal']))
    taggedValue('fubel_type',
                'adhocracy.resources.IProposal')


class ISection(IVersionableFubel):

    """Document section."""

    taggedValue('extended_sheets', set(
                ['adhocracy.sheets.document.ISection']))


class ISectionVersionsPool(IFubelVersionsPool):

    """Section Versions Pool."""

    taggedValue('addable_content_interfaces', set(
        ['adhocracy.resources.ITag',
         'adhocracy.resources.ISection']))
    taggedValue('fubel_type', 'adhocracy.resources.ISection')


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
        if IVersionableFubel.providedBy(resource):
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
    """Register factories in substanced content registry.

    Iterate all resource interfaces and automatically register factories.

    """
    resources = sys.modules[__name__]
    ifaces = get_ifaces_from_module(resources, base=IResource)
    for iface in ifaces:
        name = iface.queryTaggedValue('content_name') or iface.__identifier__
        meta = {
            'content_name': name,
            'add_view': 'add_' + iface.__identifier__,
        }
        add_content_type(config, iface.__identifier__,
                         ResourceFactory(iface),
                         factory_type=iface.__identifier__, **meta)
