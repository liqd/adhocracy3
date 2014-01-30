from pyramid import testing
import unittest


##########
#  tests #
##########

class TagsPropertySheetAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.tags')

    def tearDown(self):
        testing.tearDown()

    def get_one(self, config, context, iface):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        inst = config.registry.getMultiAdapter((context, iface),
                                               IResourcePropertySheet)
        return inst

    def test_includeme_register_ipropertysheet_adapter_itags(self):
        from adhocracy.sheets.tags import ITags
        inst = self.get_one(self.config, testing.DummyResource(), ITags)
        assert inst.iface is ITags

    def test_includeme_register_ipropertysheet_adapter_itag(self):
        from adhocracy.sheets.tags import ITag
        inst = self.get_one(self.config, testing.DummyResource(), ITag)
        assert inst.iface is ITag
