from adhocracy.interfaces import ISheet
from pyramid.testing import DummyResource
from unittest.mock import patch
from pyramid import testing
from zope.interface import taggedValue
import colander
import pytest
import unittest


############
#  helper  #
############


class ISheetB(ISheet):
    taggedValue('schema', 'adhocracy.sheets.test_pool.CountSchema')


class CountSchema(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                default=0,
                                missing=colander.drop)


@patch('substanced.objectmap.ObjectMap', autospec=True)
def make_folder_with_objectmap(dummyobjectmap=None):
    folder = testing.DummyResource()
    folder.__objectmap__ = dummyobjectmap.return_value
    return folder


##########
#  tests #
##########


class PoolPropertySheetUnitTest(unittest.TestCase):

    def make_one(self, *args):
        from .pool import PoolPropertySheetAdapter
        return PoolPropertySheetAdapter(*args)

    def test_create_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface.verify import verifyObject
        from adhocracy.sheets.pool import IPool
        from pyramid.httpexceptions import HTTPNotImplemented
        inst = self.make_one(DummyResource(), IPool)
        assert verifyObject(IResourcePropertySheet, inst) is True
        with pytest.raises(HTTPNotImplemented):
            inst.set_cstruct({})
        with pytest.raises(HTTPNotImplemented):
            inst.set({})

    def test_create_non_valid(self):
        with pytest.raises(AssertionError):
            self.make_one(DummyResource(), ISheetB)

    def test_get_empty(self):
        from adhocracy.sheets.pool import IPool
        context = make_folder_with_objectmap()
        context.__objectmap__.pathlookup.return_value = []
        inst = self.make_one(context, IPool)
        assert inst.get() == {'elements': []}

    def test_get_not_empty(self):
        from adhocracy.sheets.pool import IPool
        context = make_folder_with_objectmap()
        context.__objectmap__.pathlookup.return_value = [1]
        context['child1'] = DummyResource()
        inst = self.make_one(context, IPool)
        assert inst.get() == {'elements': [1]}


class PoolPropertySheetAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def make_one(self, config, context, iface):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        inst = config.registry.getMultiAdapter((context, iface),
                                               IResourcePropertySheet)
        return inst

    def test_includeme_register_ipropertysheet_adapter_ipool(self):
        from adhocracy.sheets.pool import IPool
        from adhocracy.sheets.pool import PoolPropertySheetAdapter
        self.config.include('adhocracy.sheets.pool')
        inst = self.make_one(self.config, DummyResource(), IPool)
        assert isinstance(inst, PoolPropertySheetAdapter)
        assert inst.iface is IPool
