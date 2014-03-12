from pyramid import testing
from zope.interface.verify import verifyObject

import unittest


class ItemNewVersionAddedUnitTest(unittest.TestCase):

    def _makeOne(self, *arg):
        from . import ItemNewVersionAdded
        return ItemNewVersionAdded(*arg)

    def test_create(self):
        from adhocracy.interfaces import IItemNewVersionAdded
        obj = testing.DummyResource()
        old_version = testing.DummyResource()
        new_version = testing.DummyResource()

        inst = self._makeOne(obj, old_version, new_version)

        assert IItemNewVersionAdded.providedBy(inst)
        assert verifyObject(IItemNewVersionAdded, inst)


class SheetReferencedItemHasNewVersionUnitTest(unittest.TestCase):

    def _makeOne(self, *arg):
        from . import SheetReferencedItemHasNewVersion
        return SheetReferencedItemHasNewVersion(*arg)

    def test_create(self):
        from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
        from adhocracy.interfaces import ISheet
        obj = testing.DummyResource()
        isheet = ISheet
        isheet_field = 'example_field'
        old_version_oid = 5
        new_version_oid = 6

        inst = self._makeOne(obj, isheet, isheet_field,
                             old_version_oid, new_version_oid)

        assert ISheetReferencedItemHasNewVersion.providedBy(inst)
        assert verifyObject(ISheetReferencedItemHasNewVersion, inst)
