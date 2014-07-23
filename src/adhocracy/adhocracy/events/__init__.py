""" Events when adding with ItemVersions and Items.

In addition we have the normal substanced events:
https://substanced.readthedocs.org/en/latest/api.html#module-substanced.event

"""
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.interfaces import IInterface

from adhocracy.interfaces import IItemVersionNewVersionAdded
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy.interfaces import IResourceCreatedAndAdded
from adhocracy.interfaces import IResourceSheetModified
from adhocracy.interfaces import ISheet


@implementer(IResourceCreatedAndAdded)
class ResourceCreatedAndAdded:

    """An event type sent when a new IResource is created and added.

    :param object(adhocracy.interfaces.IResource):
    :param parent(adhocracy.interfaces.IResource):
    :param request(pyramid.request.Request):
    """

    def __init__(self, object, parent, request):
        self.object = object
        self.parent = parent
        self.request = request


@implementer(IResourceSheetModified)
class ResourceSheetModified:

    """An event type sent when a resource sheet is modified.

    :param object(adhocracy.interfaces.IResource):
    :param isheet(adhocracy.interfaces.IISheet):
    :param request(pyramid.request.Request):
    """

    def __init__(self, object, isheet, request):
        self.object = object
        self.isheet = isheet
        self.request = request


@implementer(IItemVersionNewVersionAdded)
class ItemVersionNewVersionAdded:

    """ An event sent when a new IItemVersion is being added.

    :param object(adhocracy.interfaces.IItem):
    :param new_version(adhocracy.interfaces.IItemVersion):
    :param request(pyramid.request.Request):
    """

    def __init__(self, object, new_version, request):
        self.object = object
        self.new_version = new_version
        self.request = request


@implementer(ISheetReferencedItemHasNewVersion)
class SheetReferencedItemHasNewVersion:

    """ An event type sent when a referenced ItemVersion has a new follower.

    :param object(adhocracy.interfaces.IResource):
    :param isheet(adhocracy.interfaces.IISheet):
    :param isheet_field(str): field name with updated reference
    :param old_version(adhocracy.interfaces.IItemVersion): old referenced
                                                           resource
    :param new_version(adhocracy.interfaces.IItemVersion): new referenced
                                                           resource
    :param request(pyramid.request.Request):
    :param root_versions(list): IItemVersions not in the subtree of
                                these root resources should ignore
                                this event. Optional.
    """

    def __init__(self,
                 object,
                 isheet,
                 isheet_field,
                 old_version,
                 new_version,
                 request,
                 root_versions=[]):
        self.object = object
        self.isheet = isheet
        self.isheet_field = isheet_field
        self.old_version = old_version
        self.new_version = new_version
        self.request = request
        self.root_versions = root_versions


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
    config.add_subscriber_predicate('isheet', _ISheetPredicate)
    config.add_subscriber_predicate('interface', _InterfacePredicate)
