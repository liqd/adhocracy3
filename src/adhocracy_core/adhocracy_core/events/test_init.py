import unittest

from pyramid import testing
from zope.interface.verify import verifyObject


class ResourceCreatedAndAddedUnitTest(unittest.TestCase):

    def make_one(self, *arg):
        from adhocracy_core.events import ResourceCreatedAndAdded
        return ResourceCreatedAndAdded(*arg)

    def test_create(self):
        from adhocracy_core.interfaces import IResourceCreatedAndAdded
        context = testing.DummyResource()
        parent = testing.DummyResource()
        registry = testing.DummyResource()
        creator = testing.DummyResource()

        inst = self.make_one(context, parent, registry, creator)

        assert IResourceCreatedAndAdded.providedBy(inst)
        assert verifyObject(IResourceCreatedAndAdded, inst)


class ResourceSheetModifiedUnitTest(unittest.TestCase):

    def make_one(self, *arg):
        from adhocracy_core.events import ResourceSheetModified
        return ResourceSheetModified(*arg)

    def test_create(self):
        from adhocracy_core.interfaces import IResourceSheetModified
        context = testing.DummyResource()
        parent = testing.DummyResource()
        registry = testing.DummyResource()
        request = testing.DummyResource()
        old_appstruct = {}
        new_appstruct = {}

        inst = self.make_one(context, parent, registry, old_appstruct,
                              new_appstruct, request)

        assert IResourceSheetModified.providedBy(inst)
        assert verifyObject(IResourceSheetModified, inst)
        assert inst.object is context
        assert inst.registry is registry
        assert inst.old_appstruct is old_appstruct
        assert inst.new_appstruct is new_appstruct
        assert inst.request is request


class ItemNewVersionAddedUnitTest(unittest.TestCase):

    def make_one(self, *arg):
        from adhocracy_core.events import ItemVersionNewVersionAdded
        return ItemVersionNewVersionAdded(*arg)

    def test_create(self):
        from adhocracy_core.interfaces import IItemVersionNewVersionAdded
        context = testing.DummyResource()
        new_version = testing.DummyResource()
        registry = testing.DummyResource()
        creator = testing.DummyResource()

        inst = self.make_one(context, new_version, registry, creator)

        assert IItemVersionNewVersionAdded.providedBy(inst)
        assert verifyObject(IItemVersionNewVersionAdded, inst)


class SheetReferencedItemHasNewVersionUnitTest(unittest.TestCase):

    def make_one(self, *arg, **kwargs):
        from adhocracy_core.events import SheetReferenceNewVersion
        return SheetReferenceNewVersion(*arg, **kwargs)

    def test_create(self):
        from adhocracy_core.interfaces import ISheetReferenceNewVersion
        from adhocracy_core.interfaces import ISheet
        context = testing.DummyResource()
        isheet = ISheet
        isheet_field = 'example_field'
        old_version = testing.DummyResource()
        new_version = testing.DummyResource()
        root_versions = [context]
        registry = testing.DummyResource()
        creator = testing.DummyResource()
        is_batchmode = True

        inst = self.make_one(context, isheet, isheet_field, old_version,
                              new_version, registry, creator,
                              root_versions=root_versions,
                              is_batchmode=is_batchmode)

        assert ISheetReferenceNewVersion.providedBy(inst)
        assert verifyObject(ISheetReferenceNewVersion, inst)


def test_sheet_back_reference_added():
    from . import SheetBackReferenceAdded
    from adhocracy_core.interfaces import ISheetBackReferenceAdded
    from adhocracy_core.interfaces import ISheet
    from adhocracy_core.interfaces import Reference
    context = testing.DummyResource()
    reference = Reference(None, None, None, None)
    registry = testing.DummyResource()
    inst = SheetBackReferenceAdded(context, ISheet, reference, registry)
    assert ISheetBackReferenceAdded.providedBy(inst)
    assert verifyObject(ISheetBackReferenceAdded, inst)


def test_sheet_back_reference_removed():
    from . import SheetBackReferenceRemoved
    from adhocracy_core.interfaces import ISheetBackReferenceRemoved
    from adhocracy_core.interfaces import ISheet
    from adhocracy_core.interfaces import Reference
    context = testing.DummyResource()
    reference = Reference(None, None, None, None)
    registry = testing.DummyResource()
    inst = SheetBackReferenceRemoved(context, ISheet, reference, registry)
    assert ISheetBackReferenceRemoved.providedBy(inst)
    assert verifyObject(ISheetBackReferenceRemoved, inst)


class TestLocalRolesModified:

    def make_one(self, *arg, **kwargs):
        from . import LocalRolesModified
        return LocalRolesModified(*arg, **kwargs)

    def test_create(self):
        from adhocracy_core.interfaces import ILocalRolesModfied
        context = testing.DummyResource()
        old_local_roles = {}
        new_local_roles = {}
        registry = testing.DummyResource()
        inst = self.make_one(context, new_local_roles, old_local_roles,
                              registry)

        assert ILocalRolesModfied.providedBy(inst)
        assert verifyObject(ILocalRolesModfied, inst)


class _ISheetPredicateUnitTest(unittest.TestCase):

    def make_one(self, *arg):
        from adhocracy_core.events import _ISheetPredicate
        return _ISheetPredicate(*arg)

    def test_create(self):
        from adhocracy_core.interfaces import ISheet
        inst = self.make_one(ISheet, None)
        assert inst.isheet == ISheet

    def test_call_event_without_isheet(self):
        from adhocracy_core.interfaces import ISheet
        dummy_event = testing.DummyResource()
        inst = self.make_one(ISheet, None)
        assert not inst.__call__(dummy_event)

    def test_call_event_with_isheet(self):
        from adhocracy_core.interfaces import ISheet
        dummy_event = testing.DummyResource()
        dummy_event.isheet = ISheet
        inst = self.make_one(ISheet, None)
        assert inst.__call__(dummy_event)


class _InterfacePredicateUnitTest(unittest.TestCase):

    def make_one(self, *arg):
        from adhocracy_core.events import _InterfacePredicate
        return _InterfacePredicate(*arg)

    def test_create(self):
        from adhocracy_core.interfaces import ILocation
        inst = self.make_one(ILocation, None)
        assert inst.interface == ILocation

    def test_call_event_without_object_iface(self):
        from adhocracy_core.interfaces import ILocation
        dummy_event = testing.DummyResource()
        dummy_event.object = testing.DummyResource()
        inst = self.make_one(ILocation, None)
        assert not inst.__call__(dummy_event)

    def test_call_event_with_object_iface(self):
        from adhocracy_core.interfaces import ILocation
        dummy_event = testing.DummyResource()
        dummy_event.object = testing.DummyResource(__provides__=ILocation)
        inst = self.make_one(ILocation, None)
        assert inst.__call__(dummy_event)


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy_core.events')

    def tearDown(self):
        testing.tearDown()

    def test_register_subsriber_predicats(self):
        assert self.config.get_predlist('event_isheet')
        assert self.config.get_predlist('object_iface')
