"""Resource type configuration and default factory."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.utils import get_ifaces_from_module
from adhocracy.utils import get_all_taggedvalues
from substanced.content import add_content_type
from substanced.interfaces import IAutoNamingFolder
from zope.dottedname.resolve import resolve
from zope.interface import directlyProvides
from zope.interface import alsoProvides
from zope.interface import taggedValue
from zope.component import getMultiAdapter

import sys


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


class IVersionableFubel(IResource):

    """Versionable object, created during a Participation Process (mainly)."""

    taggedValue('content_name', 'VersionableFubel')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.INameReadOnly',
                 'adhocracy.sheets.versions.IVersionable']))


# Concrete Fubels and FubelVersionsPools

class IProposal(IVersionableFubel):

    """Versionable Fubel with Document propertysheet."""

    taggedValue('extended_sheets', set(
                ['adhocracy.sheets.document.IDocument']))


class IProposalVersionsPool(IFubelVersionsPool):

    """Proposal Versions Pool."""

    taggedValue('addable_content_interfaces', set(
        ['adhocracy.resources.ITags',
         'adhocracy.resources.IFubelVersionsPool']))
    taggedValue('fubel_content_type',
                'adhocracy.resources.IProposal')


class ISection(IVersionableFubel):

    """Document section."""


class ISectionVersionsPool(IFubelVersionsPool):

    """Section Versions Pool."""

    taggedValue('addable_content_interfaces', set(
        ['adhocracy.resources.ITags',
         'adhocracy.resources.ISection']))
    taggedValue('fubel_type', 'adhocracy.resources.ISection')


class ResourceFactory(object):

    """Basic resource factory."""

    def __init__(self, iface):
        assert iface.isOrExtends(IResource)
        taggedvalues = get_all_taggedvalues(iface)
        self.class_ = resolve(taggedvalues['content_class'])
        self.resource_iface = iface
        base_ifaces = taggedvalues['basic_sheets']
        ext_ifaces = taggedvalues['extended_sheets']
        self.prop_ifaces = [resolve(i) for i in base_ifaces.union(ext_ifaces)]
        for i in self.prop_ifaces:
            assert i.isOrExtends(ISheet)
        self.after_creation = taggedvalues['after_creation']

    def _set_appstructs(self, resource, appstructs):
        for key, struct in appstructs.items():
            iface = resolve(key)
            sheet = getMultiAdapter((resource, iface),
                                    IResourcePropertySheet)
            sheet.set(struct)

    def __call__(self, **kwargs):
        resource = self.class_()
        directlyProvides(resource, self.resource_iface)
        alsoProvides(resource, self.prop_ifaces)
        if 'appstructs' in kwargs:
            self._set_appstructs(resource, kwargs['appstructs'])
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
