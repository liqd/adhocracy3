from pyramid import testing
import unittest


##########
#  tests #
##########

class NamePropertySheetAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.name')

    def tearDown(self):
        testing.tearDown()

    def get_one(self, config, context, iface):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        inst = config.registry.getMultiAdapter((context, iface),
                                               IResourcePropertySheet)
        return inst

    def test_includeme_register_ipropertysheet_adapter_iname(self):
        from adhocracy.sheets.name import IName
        inst = self.get_one(self.config, testing.DummyResource(), IName)
        assert inst.iface is IName
