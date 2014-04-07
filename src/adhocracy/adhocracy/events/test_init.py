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
        root_versions = [obj]

        inst = self._makeOne(obj, isheet, isheet_field,
                             old_version_oid, new_version_oid,
                             root_versions)

        assert ISheetReferencedItemHasNewVersion.providedBy(inst)
        assert verifyObject(ISheetReferencedItemHasNewVersion, inst)


class _ISheetPredicateUnitTest(unittest.TestCase):

    def _makeOne(self, *arg):
        from . import _ISheetPredicate
        return _ISheetPredicate(*arg)

    def test_create(self):
        from adhocracy.interfaces import ISheet
        inst = self._makeOne(ISheet, None)
        assert inst.val == ISheet
        assert inst.config is None

    def test_call_wrong_event_type(self):
        from adhocracy.interfaces import ISheet
        dummy_event = testing.DummyResource()
        inst = self._makeOne(ISheet, None)
        result = inst.__call__(dummy_event)
        assert not result

    def test_call_right_event_type(self):
        from adhocracy.interfaces import ISheet
        from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
        from zope.interface import alsoProvides
        dummy_event = testing.DummyResource()
        alsoProvides(dummy_event, ISheetReferencedItemHasNewVersion)
        dummy_event.isheet = ISheet
        inst = self._makeOne(ISheet, None)
        result = inst.__call__(dummy_event)
        assert result


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.events')

    def tearDown(self):
        testing.tearDown()

    def test_register_subsriber_predictas(self):
        preds = self.config.get_predlist('subscriber')
        assert preds.last_added == 'isheet'
