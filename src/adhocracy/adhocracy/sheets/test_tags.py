import unittest

from pyramid import testing

from adhocracy.interfaces import IResourceSheet
from adhocracy.utils import get_sheet


class TagsSheetUnitTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.sheets.tags import tags_metadata
        self.metadata = tags_metadata
        self.context = testing.DummyResource()

    def make_one(self, *args):
        return self.metadata.sheet_class(*args)

    def test_create_valid(self):
        from zope.interface.verify import verifyObject
        from adhocracy.sheets.pool import PoolSheet
        inst = self.make_one(self.metadata, self.context)
        assert verifyObject(IResourceSheet, inst) is True
        assert isinstance(inst, PoolSheet)

    def test_get_not_empty(self):
        from adhocracy.sheets.tags import ITag
        child_tag = testing.DummyResource(__provides__=ITag)
        self.context['child'] = child_tag
        inst = self.make_one(self.metadata, self.context)
        assert inst.get() == {'elements': [child_tag]}

    def test_get_not_empty_but_no_itag(self):
        self.context['child'] = testing.DummyResource()
        inst = self.make_one(self.metadata, self.context)
        assert inst.get() == {'elements': []}


class TagsIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.tags')

    def tearDown(self):
        testing.tearDown()

    def test_includeme_register_adapter_itags(self):
        from adhocracy.sheets.tags import ITags
        context = testing.DummyResource(__provides__=ITags)
        inst = get_sheet(context, ITags)
        assert inst.meta.isheet is ITags


class TagIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.tags')

    def tearDown(self):
        testing.tearDown()

    def test_includeme_register_adapter_itag(self):
        from adhocracy.sheets.tags import ITag
        context = testing.DummyResource(__provides__=ITag)
        inst = get_sheet(context, ITag)
        assert inst.meta.isheet is ITag
