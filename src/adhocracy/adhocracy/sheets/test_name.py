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
        from adhocracy.utils import get_sheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        return get_sheet(context, iface)

    def test_includeme_register_ipropertysheet_adapter_iname(self):
        from adhocracy.sheets.name import IName
        inst = self.get_one(self.config, testing.DummyResource(), IName)
        assert inst.iface is IName
