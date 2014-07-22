import unittest

from unittest.mock import patch
from pyramid import testing

from adhocracy.interfaces import IResourceSheet
from adhocracy.utils import get_sheet


class VersionsSheetUnitTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.sheets.versions import versions_metadata
        self.metadata = versions_metadata
        self.context = testing.DummyResource()

    def _make_one(self, *args):
        return self.metadata.sheet_class(*args)

    def test_create(self):
        from adhocracy.sheets.versions import PoolSheet
        inst = self._make_one(self.metadata, self.context)
        assert isinstance(inst, PoolSheet)

    def test_get_empty(self):
        inst = self._make_one(self.metadata, self.context)
        assert inst.get() == {'elements': []}

    def test_get_not_empty(self):
        from adhocracy.sheets.versions import IVersionable
        versionable = testing.DummyResource(__provides__=IVersionable)
        self.context['child'] = versionable
        inst = self._make_one(self.metadata, self.context)
        assert inst.get() == {'elements': [versionable]}

    def test_get_not_empty_not_iversionable(self):
        non_versionable = testing.DummyResource()
        self.context['child'] = non_versionable
        inst = self._make_one(self.metadata, self.context)
        assert inst.get() == {'elements': []}


class VersionableSheetUnitTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.sheets.versions import versionable_metadata
        self.metadata = versionable_metadata
        self.context = testing.DummyResource()

    def _make_one(self, *args):
        return self.metadata.sheet_class(*args)

    def test_create_valid(self):
        from zope.interface.verify import verifyObject
        from adhocracy.sheets.versions import VersionableSheet
        inst = self._make_one(self.metadata, self.context)
        assert isinstance(inst, VersionableSheet)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self):
        inst = self._make_one(self.metadata, self.context)
        data = inst.get()
        assert list(data['follows']) == []
        assert list(data['followed_by']) == []

    @patch('adhocracy.graph.Graph')
    def test_get_with_followed_by(self, graph_dummy=None):
        successor = testing.DummyResource()
        inst = self._make_one(self.metadata, self.context)
        inst._graph = graph_dummy.return_value
        inst._graph.get_followed_by.return_value = iter([successor])
        data = inst.get()
        assert list(data['followed_by']) == [successor]

    @patch('adhocracy.graph.Graph')
    def test_get_with_follows(self, graph_dummy=None):
        precessor = testing.DummyResource()
        inst = self._make_one(self.metadata, self.context)
        inst._graph = graph_dummy.return_value
        inst._graph.get_follows.return_value = iter([precessor])
        data = inst.get()
        assert list(data['follows']) == [precessor]

    def test_set_with_followed_by(self):
        inst = self._make_one(self.metadata, self.context)
        inst.set({'followed_by': iter([])})
        assert not 'followed_by' in inst._data


class VersionsSheetIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.versions')

    def tearDown(self):
        testing.tearDown()

    def test_register_versions_sheet(self):
        from adhocracy.sheets.versions import IVersions
        context = testing.DummyResource(__provides__=IVersions)
        inst = get_sheet(context, IVersions)
        assert inst.meta.isheet is IVersions


class VersionableSheetIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.versions')

    def tearDown(self):
        testing.tearDown()

    def test_register_versionable_sheet(self):
        from adhocracy.sheets.versions import IVersionable
        context = testing.DummyResource(__provides__=IVersionable)
        inst = get_sheet(context, IVersionable)
        assert inst.meta.isheet is IVersionable
