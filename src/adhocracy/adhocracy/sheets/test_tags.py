import unittest

from pyramid import testing



############
#  helper  #
############


##########
#  tests #
##########


class TagsPropertySheetUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()

    def make_one(self, context, isheet):
        from .tags import PoolPropertySheetAdapter
        return PoolPropertySheetAdapter(context, isheet)

    def test_create_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface.verify import verifyObject
        from adhocracy.sheets.pool import PoolPropertySheetAdapter
        from adhocracy.sheets.tags import ITags
        inst = self.make_one(self.context, ITags)
        assert verifyObject(IResourcePropertySheet, inst) is True
        assert isinstance(inst, PoolPropertySheetAdapter)

    def test_get_not_empty(self):
        from adhocracy.sheets.tags import ITags
        from adhocracy.sheets.tags import ITag
        child = testing.DummyResource(__provides__=ITag, __oid__=1)
        self.context['child'] = child
        inst = self.make_one(self.context, ITags)
        assert inst.get() == {'elements': [child]}

    def test_get_not_empty_not_iversionable(self):
        from adhocracy.sheets.tags import ITags
        self.context['child'] = testing.DummyResource()
        inst = self.make_one(self.context, ITags)
        assert inst.get() == {'elements': []}


##########
#  tests #
##########

class includemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.tags')

    def tearDown(self):
        testing.tearDown()

    def get_one(self, config, context, iface):
        from adhocracy.utils import get_sheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        return get_sheet(context, iface)

    def test_includeme_register_adapter_itags(self):
        from adhocracy.sheets.tags import ITags
        from adhocracy.sheets.versions import PoolPropertySheetAdapter
        inst = self.get_one(self.config, testing.DummyResource(), ITags)
        assert isinstance(inst, PoolPropertySheetAdapter)
        assert inst.iface is ITags

    def test_includeme_register_adapter_itag(self):
        from adhocracy.sheets.tags import ITag
        inst = self.get_one(self.config, testing.DummyResource(), ITag)
        assert inst.iface is ITag
