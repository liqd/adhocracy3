""" Events when adding with ItemVersions and Items.

In addition we have the normal substanced events:
https://substanced.readthedocs.org/en/latest/api.html#module-substanced.event

"""
from adhocracy.interfaces import IItemVersionNewVersionAdded
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy.interfaces import ISheet
from zope.interface import implementer


@implementer(IItemVersionNewVersionAdded)
class ItemVersionNewVersionAdded(object):

    """ An event sent when a new IItemVersion is being added.

    Args:
        object (IVersion): old version
        new_version (IItemVersion)

    """

    def __init__(self,
                 context,
                 new_version):
        self.object = context
        self.new_version = new_version


@implementer(ISheetReferencedItemHasNewVersion)
class SheetReferencedItemHasNewVersion(object):

    """ An event type sent when a referenced ItemVersion has a new follower.

    Args:
        object (IResource)
        isheet (IISheet)
        isheet_field (str): field name with updated reference
        old_version_oid (int): old oid of referenced resource
        new_version_oid (int): new oid of referenced resource
        root_versions (list, optional): IVersionables not in the subtree of
                                        these root resources should ignore
                                        this event.

    """

    def __init__(self,
                 context,
                 isheet,
                 isheet_field,
                 old_version_oid,
                 new_version_oid,
                 root_versions=[]):
        self.object = context
        self.isheet = isheet
        self.isheet_field = isheet_field
        self.old_version_oid = old_version_oid
        self.new_version_oid = new_version_oid
        self.root_versions = root_versions


class _ISheetPredicate(object):

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
