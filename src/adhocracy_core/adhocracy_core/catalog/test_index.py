"""Test custom catalog index."""
from unittest.mock import Mock
from pyramid import testing
from pytest import fixture
from pytest import raises


class TestField:

    _marker = object()

    @fixture
    def inst(self):
        from hypatia.field import FieldIndex
        from BTrees import family64

        def _discriminator(obj, default):
            if obj is self._marker:
                return default
            return obj
        return FieldIndex(_discriminator, family64)

    def test_sort_integer_strings(self, inst):
        inst.index_doc(0, '-1')
        inst.index_doc(3, '10')
        inst.index_doc(1, '1')
        assert [x for x in inst.sort([0, 3, 1])] == [0, 1, 3]



class TestReference:

    @fixture
    def catalog(self):
        from substanced.interfaces import IService
        catalog = testing.DummyResource(__provides__=IService,
                                        __is_service__=True)
        return catalog

    @fixture
    def context(self, pool_graph, catalog):
        pool_graph['catalogs'] = catalog
        return pool_graph

    def make_one(self):
        from .index import ReferenceIndex
        index = ReferenceIndex()
        return index

    def test_create(self):
        from zope.interface.verify import verifyObject
        from hypatia.interfaces import IIndex
        inst = self.make_one()
        assert IIndex.providedBy(inst)
        assert verifyObject(IIndex, inst)

    def test_reset(self):
        inst = self.make_one()
        inst._not_indexed.add(1)
        inst.reset()
        assert 1 not in inst._not_indexed

    def test_document_repr(self, context, catalog):
        from substanced.util import get_oid
        inst = self.make_one()
        catalog['index'] = inst
        assert inst.document_repr(get_oid(context)) == ('',)

    def test_document_repr_missing(self, context, catalog):
        inst = self.make_one()
        catalog['index'] = inst
        assert inst.document_repr(1) is None

    def test_index_doc(self):
         inst = self.make_one()
         assert inst.index_doc(1, None) is None

    def test_unindex_doc(self):
         inst = self.make_one()
         assert inst.unindex_doc(1) is None

    def test_reindex_doc(self):
        inst = self.make_one()
        assert inst.reindex_doc(1, None) is None

    def test_docids(self, context, catalog):
         inst = self.make_one()
         catalog['index'] = inst
         assert list(inst.docids()) == []

    def test_not_indexed(self):
         inst = self.make_one()
         assert list(inst.not_indexed()) == []

    def test_search_raise_if_source_and_target_is_none(self):
         from adhocracy_core.interfaces import Reference
         from adhocracy_core.interfaces import ISheet
         inst = self.make_one()
         reference = Reference(None, ISheet, '', None)
         with raises(ValueError):
            inst._search(reference)

    def test_search_raise_if_source_and_target_is_not_none(self):
         from adhocracy_core.interfaces import Reference
         from adhocracy_core.interfaces import ISheet
         inst = self.make_one()
         reference = Reference(object(), ISheet, '', object())
         with raises(ValueError):
            inst._search(reference)

    def test_search_sources(self, mock_graph):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import Reference
        target = testing.DummyResource()
        mock_graph.get_source_ids.return_value = {1}
        inst = self.make_one()
        inst.__graph__ = mock_graph
        reference = Reference(None, ISheet, '', target)
        result = inst._search(reference)
        mock_graph.get_source_ids.assert_called_with(target, ISheet, '')
        assert list(result) == [1]

    def test_search_targets(self, mock_graph):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import Reference
        source = testing.DummyResource()
        mock_graph.get_target_ids.return_value = {1}
        inst = self.make_one()
        inst.__graph__ = mock_graph
        reference = Reference(source, ISheet, '', None)
        result = inst._search(reference)
        mock_graph.get_target_ids.assert_called_with(source, ISheet, '')
        assert list(result) == [1]

    def test_apply_with_valid_query(self, mock_graph):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import Reference
        mock_graph.get_source_ids.return_value = {1}
        inst = self.make_one()
        inst.__graph__ = mock_graph
        target = testing.DummyResource()
        reference = Reference(None, ISheet, '', target)
        query = {'reference': reference}
        result = inst.apply(query)
        assert list(result) == [1]

    def test_apply_with_invalid_query(self):
        inst = self.make_one()
        query = {'WRONG': ''}
        with raises(KeyError):
            inst.apply(query)

    def test_apply_intersect_reference_not_exists(self):
        # actually we test the default implementation in hypatia.util
        import BTrees
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import Reference
        from adhocracy_core.graph import Graph
        graph = Mock(spec=Graph)
        graph.get_source_ids.return_value = set()
        inst = self.make_one()
        inst.__graph__ = graph
        target = testing.DummyResource()
        reference = Reference(None, ISheet, '', target)
        query = {'reference': reference}
        other_result = BTrees.family64.IF.Set([1])
        result = inst.apply_intersect(query, other_result)
        assert list(result) == []

    def test_eq(self):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import Reference
        inst = self.make_one()
        target = testing.DummyResource()
        reference = Reference(None, ISheet, '', target)
        result = inst.eq(reference)
        assert result._value == {'reference': reference}
