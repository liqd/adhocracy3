from pyramid import testing
import pytest
import unittest


############
#  helper  #
############


##########
#  tests #
##########


class PoolPropertySheetUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()

    def make_one(self, context, isheet):
        from .pool import PoolPropertySheetAdapter
        return PoolPropertySheetAdapter(context, isheet)

    def test_create_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface.verify import verifyObject
        from adhocracy.sheets.pool import IPool
        from pyramid.httpexceptions import HTTPNotImplemented
        inst = self.make_one(self.context, IPool)
        assert verifyObject(IResourcePropertySheet, inst) is True
        with pytest.raises(HTTPNotImplemented):
            inst.validate_cstruct({})
        with pytest.raises(HTTPNotImplemented):
            inst.set({})

    def test_get_empty(self):
        from adhocracy.sheets.pool import IPool
        inst = self.make_one(self.context, IPool)
        assert inst.get() == {'elements': []}

    def test_get_not_empty(self):
        from adhocracy.sheets.pool import IPool
        from adhocracy.interfaces import IResource
        self.context['child1'] = testing.DummyResource(__provides__=IResource,
                                                       __oid__=1)
        inst = self.make_one(self.context, IPool)
        assert inst.get() == {'elements': [1]}

    def test_get_not_empty_not_iresource(self):
        from adhocracy.sheets.pool import IPool
        self.context['child1'] = testing.DummyResource()
        inst = self.make_one(self.context, IPool)
        assert inst.get() == {'elements': []}


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def get_one(self, config, context, iface):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        inst = config.registry.getMultiAdapter((context, iface),
                                               IResourcePropertySheet)
        return inst

    def test_includeme_register_pool_adapter(self):
        from adhocracy.sheets.pool import IPool
        from adhocracy.sheets.pool import PoolPropertySheetAdapter
        self.config.include('adhocracy.sheets.pool')
        inst = self.get_one(self.config, testing.DummyResource(), IPool)
        assert isinstance(inst, PoolPropertySheetAdapter)
        assert inst.iface is IPool
