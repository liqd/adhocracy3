""" Events when adding with ItemVersions and Items.

In addition we have the normal substanced events:
https://substanced.readthedocs.org/en/latest/api.html#module-substanced.event

"""
from zope.interface import implementer

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
    :param registry(pyramid.registry.Registry):
    """

    def __init__(self, object, parent, registry):
        self.object = object
        self.parent = parent
        self.registry = registry


@implementer(IResourceSheetModified)
class ResourceSheetModified:

    """An event type sent when a resource sheet is modified.

    :param object(adhocracy.interfaces.IResource):
    :param isheet(adhocracy.interfaces.IISheet):
    :param registry(pyramid.registry.Registry):
    """

    def __init__(self, object, isheet, registry):
        self.object = object
        self.isheet = isheet
        self.registry = registry


@implementer(IItemVersionNewVersionAdded)
class ItemVersionNewVersionAdded:

    """ An event sent when a new IItemVersion is being added.

    :param object(adhocracy.interfaces.IItem):
    :param new_version(adhocracy.interfaces.IItemVersion):
    :param registry(pyramid.registry.Registry):
    """

    def __init__(self, object, new_version, registry):
        self.object = object
        self.new_version = new_version
        self.registry = registry


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
    :param registry(pyramid.registry.Registry):
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
                 registry,
                 root_versions=[]):
        self.object = object
        self.isheet = isheet
        self.isheet_field = isheet_field
        self.old_version = old_version
        self.new_version = new_version
        self.registry = registry
        self.root_versions = root_versions


class _ISheetPredicate:

    """Allow to register event subscriber with the 'isheet' predicate."""

    def __init__(self, val, config):
        assert val.isOrExtends(ISheet)
        self.val = val
        self.config = config

    def phash(self):
        """Return text representation."""
        return 'isheet = %s' % (self.val,)

    text = phash

    def __call__(self, event):
        result = False
        if ISheetReferencedItemHasNewVersion.providedBy(event):
            if event.isheet.isOrExtends(self.val):
                result = True
        return result


def includeme(config):
    """ register event subscriber predicate 'isheet'."""
    config.add_subscriber_predicate('isheet', _ISheetPredicate)
