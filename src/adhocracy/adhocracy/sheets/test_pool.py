import unittest

from pyramid import testing
import pytest

from adhocracy.interfaces import IResourceSheet
from adhocracy.interfaces import ISheet
from adhocracy.utils import get_sheet


class PoolSheetUnitTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.sheets.pool import pool_metadata
        self.metadata = pool_metadata
        self.context = testing.DummyResource()

    def _make_one(self, *args):
        return self.metadata.sheet_class(*args)

    def test_create_valid(self):
        from pyramid.httpexceptions import HTTPNotImplemented
        from zope.interface.verify import verifyObject
        from adhocracy.sheets.pool import PoolSheet

        inst = self._make_one(self.metadata, self.context)

        assert isinstance(inst, PoolSheet)
        assert verifyObject(IResourceSheet, inst) is True
        with pytest.raises(HTTPNotImplemented):
            inst.set({})

    def test_get_empty(self):
        inst = self._make_one(self.metadata, self.context)
        assert inst.get() == {'elements': []}

    def test_get_not_empty_with_target_isheet(self):
        child = testing.DummyResource(__provides__=ISheet)
        self.context['child1'] = child
        inst = self._make_one(self.metadata, self.context)
        assert inst.get() == {'elements': [child]}

    def test_get_not_empty_without_iresource(self):
        self.context['child1'] = testing.DummyResource()
        inst = self._make_one(self.metadata, self.context)
        assert inst.get() == {'elements': []}


class PoolSheetIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.pool')

    def tearDown(self):
        testing.tearDown()

    def test_includeme_register_pool_adapter(self):
        from adhocracy.sheets.pool import IPool
        context = testing.DummyResource(__provides__=IPool)
        inst = get_sheet(context, IPool)
        assert inst.meta.isheet == IPool


