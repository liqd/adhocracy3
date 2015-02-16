"""Hooks to modify runtime behavior (use 'subscriber.py' in you package).

In addition we have the normal substanced events:
https://substanced.readthedocs.org/en/latest/api.html#module-substanced.event

"""
from pyramid.request import Request
from pyramid.registry import Registry
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.interfaces import IInterface

from adhocracy_core.interfaces import IItemVersionNewVersionAdded
from adhocracy_core.interfaces import ISheetReferenceNewVersion
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.interfaces import ILocalRolesModfied
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetBackReferenceAdded
from adhocracy_core.interfaces import ISheetBackReferenceRemoved


@implementer(IResourceCreatedAndAdded)
class ResourceCreatedAndAdded:

    """An event type sent when a new IResource is created and added.

    :param object(adhocracy_core.interfaces.IResource):
    :param parent(adhocracy_core.interfaces.IResource):
    :param registry(pyramid.registry.Registry):
    :param creator(adhocracy_core.resource.principal.IUser):
    """

    def __init__(self, object, parent, registry, creator):
        self.object = object
        self.parent = parent
        self.registry = registry
        self.creator = creator


@implementer(IResourceSheetModified)
class ResourceSheetModified:

    """An event type sent when a resource sheet is modified.

    :param object: adhocracy_core.interfaces.IResource
    :param isheet: adhocracy_core.interfaces.IISheet
    :param registry: pyramid.registry.Registry
    :param old_appstruct: The old :term:`appstruct` data (dict)
    :param new_appstruct: The new :term:`appstruct` data (dict)
    :param request: The current request or None
    """

    def __init__(self,
                 object,
                 isheet,
                 registry,
                 old_appstruct,
                 new_appstruct,
                 request: Request):
        self.object = object
        self.isheet = isheet
        self.registry = registry
        self.old_appstruct = old_appstruct
        self.new_appstruct = new_appstruct
        self.request = request


@implementer(IItemVersionNewVersionAdded)
class ItemVersionNewVersionAdded:

    """ An event sent when a new IItemVersion is being added.

    :param object(adhocracy_core.interfaces.IItem):
    :param new_version(adhocracy_core.interfaces.IItemVersion):
    :param registry(pyramid.registry.Registry):
    :param creator(adhocracy_core.resource.principal.IUser':
    """

    def __init__(self, object, new_version, registry, creator):
        self.object = object
        self.new_version = new_version
        self.registry = registry
        self.creator = creator


@implementer(ISheetReferenceNewVersion)
class SheetReferenceNewVersion:

    """ An event type sent when a referenced ItemVersion has a new follower.

    :param object(adhocracy_core.interfaces.IResource):
    :param isheet(adhocracy_core.interfaces.IISheet):
    :param isheet_field(str): field name with updated reference
    :param old_version(adhocracy_core.interfaces.IItemVersion): old referenced
                                                           resource
    :param new_version(adhocracy_core.interfaces.IItemVersion): new referenced
                                                           resource
    :param registry(pyramid.registry.Registry):
    :param root_versions(list): IItemVersions not in the subtree of
                                these root resources should ignore
                                this event. Optional.
    :param creator(adhocracy_core.resource.principal.IUser':

    :param is_batchmode(bool): Flag to do sheet autoupdates in batch request
                               mode. Defaults to False.
    """

    def __init__(self,
                 object,
                 isheet,
                 isheet_field,
                 old_version,
                 new_version,
                 registry,
                 creator,
                 root_versions=[],
                 is_batchmode=False,
                 ):
        self.object = object
        self.isheet = isheet
        self.isheet_field = isheet_field
        self.old_version = old_version
        self.new_version = new_version
        self.registry = registry
        self.creator = creator
        self.root_versions = root_versions
        self.is_batchmode = is_batchmode


@implementer(ISheetBackReferenceRemoved)
class SheetBackReferenceRemoved:

    """An event type sent when a back reference is removed."""

    def __init__(self,
                 object,
                 isheet,
                 reference,
                 registry,
                 ):
        self.object = object
        """:class:`adhocracy_core.interfaces.IResource`"""
        self.isheet = isheet
        """:class:`adhocracy_core.interfaces.ISheet`"""
        self.reference = reference
        """:class:`adhocracy_core.graph.Reference` that was targeting `object`.
        """
        self.registry = registry
        """:class:`pyramid.content.Registry`"""


@implementer(ISheetBackReferenceAdded)
class SheetBackReferenceAdded:

    """An event type sent when a back reference is added."""

    def __init__(self,
                 object,
                 isheet,
                 reference,
                 registry,
                 ):
        self.object = object
        """:class:`adhocracy_core.interfaces.IResource`"""
        self.isheet = isheet
        """:class:`adhocracy_core.interfaces.ISheet`"""
        self.reference = reference
        """:class:`adhocracy_core.graph.Reference` that is targeting `object`.
        """
        self.registry = registry
        """:class:`pyramid.content.Registry`"""


@implementer(ILocalRolesModfied)
class LocalRolesModified:

    """An event type send when an resource`s :term:`local role` is modified."""

    def __init__(self, object, new_local_roles: dict, old_local_roles: dict,
                 registry: Registry):
        self.object = object
        self.new_local_roles = new_local_roles
        self.old_local_roles = old_local_roles
        self.registry = registry


class _ISheetPredicate:

    """Subscriber predicate  'isheet' to check event.isheet."""

    def __init__(self, isheet: IInterface, config):
        assert isheet.isOrExtends(ISheet)
        self.isheet = isheet

    def text(self) -> str:
        """Return text representation."""
        return 'isheet = %s' % (self.isheet.__identifier__)

    phash = text

    def __call__(self, event):
        event_isheet = getattr(event, 'isheet', Interface)
        return event_isheet.isOrExtends(self.isheet)


class _InterfacePredicate:

    """Subscriber predicate 'interface' to check interfaces of event.object."""

    def __init__(self, interface: IInterface, config):
        assert interface.isOrExtends(Interface)
        self.interface = interface

    def text(self) -> str:
        """Return text representation."""
        return 'interface = %s' % (self.interface.__identifier__)

    phash = text

    def __call__(self, event):
        return self.interface.providedBy(event.object)


def includeme(config):
    """ register event subscriber predicates 'isheet' and 'interface'."""
    config.include('substanced.event')
    config.add_subscriber_predicate('isheet', _ISheetPredicate)
    config.add_subscriber_predicate('interface', _InterfacePredicate)
