import unittest

from pyramid import testing
from zope.interface.verify import verifyObject


class ResourceCreatedAndAddedUnitTest(unittest.TestCase):

    def _make_one(self, *arg):
        from adhocracy.events import ResourceCreatedAndAdded
        return ResourceCreatedAndAdded(*arg)

    def test_create(self):
        from adhocracy.interfaces import IResourceCreatedAndAdded
        context = testing.DummyResource()
        parent = testing.DummyResource()
        registry = testing.DummyResource()

        inst = self._make_one(context, parent, registry)

        assert IResourceCreatedAndAdded.providedBy(inst)
        assert verifyObject(IResourceCreatedAndAdded, inst)


class ResourceSheetModifiedUnitTest(unittest.TestCase):

    def _make_one(self, *arg):
        from adhocracy.events import ResourceSheetModified
        return ResourceSheetModified(*arg)

    def test_create(self):
        from adhocracy.interfaces import IResourceSheetModified
        context = testing.DummyResource()
        parent = testing.DummyResource()
        registry = testing.DummyResource()

        inst = self._make_one(context, parent, registry)

        assert IResourceSheetModified.providedBy(inst)
        assert verifyObject(IResourceSheetModified, inst)


class ItemNewVersionAddedUnitTest(unittest.TestCase):

    def _make_one(self, *arg):
        from adhocracy.events import ItemVersionNewVersionAdded
        return ItemVersionNewVersionAdded(*arg)

    def test_create(self):
        from adhocracy.interfaces import IItemVersionNewVersionAdded
        context = testing.DummyResource()
        new_version = testing.DummyResource()
        registry = testing.DummyResource()


        inst = self._make_one(context, new_version, registry)

        assert IItemVersionNewVersionAdded.providedBy(inst)
        assert verifyObject(IItemVersionNewVersionAdded, inst)


class SheetReferencedItemHasNewVersionUnitTest(unittest.TestCase):

    def _make_one(self, *arg):
        from adhocracy.events import SheetReferencedItemHasNewVersion
        return SheetReferencedItemHasNewVersion(*arg)

    def test_create(self):
        from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
        from adhocracy.interfaces import ISheet
        context = testing.DummyResource()
        isheet = ISheet
        isheet_field = 'example_field'
        old_version = testing.DummyResource()
        new_version = testing.DummyResource()
        root_versions = [context]
        registry = testing.DummyResource()

        inst = self._make_one(context, isheet, isheet_field, old_version,
                              new_version, root_versions, registry)

        assert ISheetReferencedItemHasNewVersion.providedBy(inst)
        assert verifyObject(ISheetReferencedItemHasNewVersion, inst)


class _ISheetPredicateUnitTest(unittest.TestCase):

    def _make_one(self, *arg):
        from adhocracy.events import _ISheetPredicate
        return _ISheetPredicate(*arg)

    def test_create(self):
        from adhocracy.interfaces import ISheet
        inst = self._make_one(ISheet, None)
        assert inst.val == ISheet
        assert inst.config is None

    def test_call_wrong_event_type(self):
        from adhocracy.interfaces import ISheet
        dummy_event = testing.DummyResource()
        inst = self._make_one(ISheet, None)
        result = inst.__call__(dummy_event)
        assert not result

    def test_call_right_event_type(self):
        from adhocracy.interfaces import ISheet
        from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
        from zope.interface import alsoProvides
        dummy_event = testing.DummyResource()
        alsoProvides(dummy_event, ISheetReferencedItemHasNewVersion)
        dummy_event.isheet = ISheet
        inst = self._make_one(ISheet, None)
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
