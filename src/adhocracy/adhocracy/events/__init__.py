""" Events when adding with ItemVersions and Items.

In addition we have the normal substanced events:
https://substanced.readthedocs.org/en/latest/api.html#module-substanced.event

"""
from adhocracy.interfaces import IItemNewVersionAdded
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from zope.interface import implementer


@implementer(IItemNewVersionAdded)
class ItemNewVersionAdded(object):

    """ An event sent when a new ITemVersion is being added."""

    def __init__(self,
                 object,
                 old_version,
                 new_version):
        self.object = object
        self.old_version = old_version
        self.new_version = new_version


@implementer(ISheetReferencedItemHasNewVersion)
class SheetReferencedItemHasNewVersion(object):

    """ An event type sent when a referenced ItemVersion has a new follower."""

    def __init__(self,
                 object,
                 isheet,
                 isheet_field,
                 old_version_oid,
                 new_version_oid):
        self.object = object
        self.isheet = isheet
        self.isheet_field = isheet_field
        self.old_version_oid = old_version_oid
        self.new_version_oid = new_version_oid
