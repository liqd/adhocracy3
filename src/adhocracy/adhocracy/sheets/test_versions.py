from pyramid import testing
import unittest


############
#  helper  #
############


##########
#  tests #
##########


class VersionsPropertySheetUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()

    def make_one(self, context):
        from adhocracy.sheets.versions import IVersions
        from .versions import PoolPropertySheetAdapter
        return PoolPropertySheetAdapter(context, IVersions)

    def test_create_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from adhocracy.sheets.pool import PoolPropertySheetAdapter
        from zope.interface.verify import verifyObject
        inst = self.make_one(self.context)
        assert verifyObject(IResourcePropertySheet, inst) is True
        assert isinstance(inst, PoolPropertySheetAdapter)

    def test_get_empty(self):
        inst = self.make_one(self.context)
        assert inst.get() == {'elements': []}

    def test_get_not_empty(self):
        from adhocracy.sheets.versions import IVersionable
        versionable = testing.DummyResource(__provides__=IVersionable,
                                            __oid__=1)
        self.context['child'] = versionable
        inst = self.make_one(self.context)
        assert inst.get() == {'elements': [1]}

    def test_get_not_empty_not_iversionable(self):
        non_versionable = testing.DummyResource()
        self.context['child'] = non_versionable
        inst = self.make_one(self.context)
        assert inst.get() == {'elements': []}


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def get_one(self, config, context, iface):
        from adhocracy.utils import get_sheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        return get_sheet(context, iface)

    def test_register_versions_adapter(self):
        from adhocracy.sheets.versions import IVersions
        from adhocracy.sheets.versions import PoolPropertySheetAdapter
        self.config.include('adhocracy.sheets.versions')
        inst = self.get_one(self.config, testing.DummyResource(), IVersions)
        assert isinstance(inst, PoolPropertySheetAdapter)
        assert inst.iface is IVersions

    def test_register_versionable_adapter(self):
        from adhocracy.sheets.versions import IVersionable
        from adhocracy.sheets.versions import ResourcePropertySheetAdapter
        self.config.include('adhocracy.sheets.versions')
        inst = self.get_one(self.config, testing.DummyResource(), IVersionable)
        assert isinstance(inst, ResourcePropertySheetAdapter)
        assert inst.iface is IVersionable
