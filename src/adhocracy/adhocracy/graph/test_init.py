import unittest
from mock import patch

from pyramid import testing
import pytest
from zope.interface import taggedValue
from zope.interface import Interface

from adhocracy.interfaces import IResource
from adhocracy.interfaces import SheetReference
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import NewVersionToOldVersion


############
#  helper  #
############


def create_dummy_resource(parent=None, iface=IResource):
    """Create dummy resource and add it to the parent objectmap."""
    from pyramid.traversal import resource_path_tuple
    from substanced.util import find_objectmap
    res = testing.DummyResource(__parent__=parent,
                                __provides__=iface,)
    om = find_objectmap(parent)
    if om:
        oid = om.new_objectid()
        res.__oid__ = oid
        res.__name__ = str(oid)
        path = resource_path_tuple(res)
        om.add(res, path)
        parent[res.__name__] = res
    return res


##########
#  tests #
##########

class TestGraphUnitTest(unittest.TestCase):

    def _make_one(self, *args):
        from adhocracy.graph import Graph
        return Graph(*args)

    def test_create(self):
        from persistent import Persistent
        dummy_objectmap = object()
        root = testing.DummyResource(__objectmap__=dummy_objectmap)
        graph = self._make_one(root)
        assert issubclass(graph.__class__, Persistent)
        assert graph._root is root
        assert graph._objectmap is root.__objectmap__

    def test_create_with_missing_objectmap(self):
        root = testing.DummyResource()
        graph = self._make_one(root)
        assert graph._objectmap is None

    def test_create_with_root_is_none(self):
        root = None
        graph = self._make_one(root)
        assert graph._root is None


class TestGraphGetReferencesUnitTest(unittest.TestCase):

    @patch('substanced.objectmap.ObjectMap', autospec=True)
    def setUp(self, dummy_objectmap=None):
        self.objectmap = dummy_objectmap.return_value

    def _make_one(self, **kwargs):
        from adhocracy.graph import Graph
        graph = Graph(None)
        graph._objectmap = self.objectmap
        return Graph.get_reftypes(graph, **kwargs)

    def test_get_reftypes_no_objectmap(self):
        self.objectmap = None
        assert list(self._make_one()) == []

    def test_get_reftypes_no_reftpyes(self):
        self.objectmap.get_reftypes.return_value = []
        assert list(self._make_one()) == []

    def test_get_reftypes_one_wrong_str_reftype(self):
        self.objectmap.get_reftypes.return_value = ["NoneSheetToSheet"]
        assert list(self._make_one()) == []

    def test_get_reftypes_one_wrong_no_sheetreference_reftype(self):
        self.objectmap.get_reftypes.return_value = [Interface]
        assert list(self._make_one()) == []

    def test_get_reftypes_one_wrong_source_isheet(self):
        class SubSheetToSheet(SheetToSheet):
            source_isheet = Interface
        self.objectmap.get_reftypes.return_value = [SubSheetToSheet]
        assert list(self._make_one()) == []

    def test_get_reftypes_one_valid_reftype(self):
        self.objectmap.get_reftypes.return_value = [SheetToSheet]
        reftypes = list(self._make_one())
        assert len(reftypes) == 1
        assert reftypes[0] == (ISheet, '', SheetToSheet)

    def test_get_reftypes_with_base_reftype(self):
        class SubSheetToSheet(SheetToSheet):
            pass
        self.objectmap.get_reftypes.return_value = [SubSheetToSheet,
                                                    SheetToSheet]
        reftypes = list(self._make_one(base_reftype=SubSheetToSheet))
        assert len(reftypes) == 1

    def test_get_reftypes_with_base_reftype_that_has_subclass(self):
        class SubSheetToSheet(SheetToSheet):
            pass
        self.objectmap.get_reftypes.return_value = [SubSheetToSheet,
                                                    SheetToSheet]
        reftypes = list(self._make_one(base_reftype=SheetToSheet))
        assert len(reftypes) == 2

    def test_get_reftypes_with_base_isheet(self):
        class ISheetA(ISheet):
            pass

        class SubSheetToSheet(SheetToSheet):
            source_isheet = ISheetA

        self.objectmap.get_reftypes.return_value = [SubSheetToSheet,
                                                    SheetToSheet]
        reftypes = list(self._make_one(base_isheet=ISheetA))
        assert len(reftypes) == 1

    def test_get_reftypes_with_base_isheet_that_has_subclass(self):
        class ISheetA(ISheet):
            pass

        class SubSheetToSheet(SheetToSheet):
            source_isheet = ISheetA

        self.objectmap.get_reftypes.return_value = [SubSheetToSheet,
                                                    SheetToSheet]
        reftypes = list(self._make_one(base_isheet=ISheet))
        assert len(reftypes) == 2


class GraphSetReferencesUnitTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.source = create_dummy_resource(parent=context)
        self.target = create_dummy_resource(parent=context)
        self.target1 = create_dummy_resource(parent=context)
        self.target2 = create_dummy_resource(parent=context)
        self.objectmap = context.__objectmap__

    def _make_one(self, *args):
        from adhocracy.graph import Graph
        graph = Graph(None)
        graph._objectmap = self.objectmap
        return Graph.set_references(graph, *args)

    def test_reftype_not_sheetreferencetype(self):
        from substanced.interfaces import ReferenceType
        with pytest.raises(AssertionError):
            self._make_one(self.source, [], ReferenceType)

    def test_targets_empty_list(self):
        self._make_one(self.source, [], SheetReference)
        references = self.objectmap.targetids(self.source, SheetReference)
        wanted_refs = []
        assert wanted_refs == list(references)

    def test_targets_list(self):
        targets = [self.target]
        self._make_one(self.source, targets, SheetReference)
        references = self.objectmap.targetids(self.source, SheetReference)
        wanted_references = [self.target.__oid__]
        assert wanted_references == list(references)

    def test_targets_list_ordered(self):
        targets = [self.target, self.target1, self.target2]
        self._make_one(self.source, targets, SheetReference)
        targets_reverse = [self.target2, self.target1, self.target]
        self._make_one(self.source, targets_reverse, SheetReference)

        references = self.objectmap.targetids(self.source, SheetReference)
        wanted_references = [x.__oid__ for x in targets_reverse]
        assert wanted_references == list(references)

    def test_targets_list_duplicated_targets(self):
        """Duplication targets are not possible with substanced.objectmap."""
        targets = [self.target, self.target]
        self._make_one(self.source, targets, SheetReference)
        references = self.objectmap.targetids(self.source, SheetReference)
        wanted_references = [self.target.__oid__]
        assert wanted_references == list(references)

    def test_targets_list_with_some_removed(self):
        targets = [self.target, self.target1, self.target2]
        self._make_one(self.source, targets, SheetReference)
        targets_some_removed = [self.target]
        self._make_one(self.source, targets_some_removed, SheetReference)

        references = self.objectmap.targetids(self.source, SheetReference)
        wanted_references = [x.__oid__ for x in targets_some_removed]
        assert wanted_references == list(references)

    def test_targets_set(self):
        targets = {self.target}
        self._make_one(self.source, targets, SheetReference)
        references = self.objectmap.targetids(self.source, SheetReference)
        wanted_references = [self.target.__oid__]
        assert wanted_references == list(references)

    def test_targets_set_duplicated_targets(self):
        targets = {self.target, self.target}
        self._make_one(self.source, targets, SheetReference)
        references = self.objectmap.targetids(self.source, SheetReference)
        wanted_references = [self.target.__oid__]
        assert wanted_references == list(references)

    def test_targets_set_with_some_removed(self):
        targets = {self.target, self.target1, self.target2}
        self._make_one(self.source, targets, SheetReference)
        targets_some_removed = {self.target}
        self._make_one(self.source, targets_some_removed, SheetReference)

        references = self.objectmap.targetids(self.source, SheetReference)
        wanted_references = [x.__oid__ for x in targets_some_removed]
        assert wanted_references == list(references)


class GraphGetReferencesUnitTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap_method = ObjectMap.sources
        self.objectmap = context.__objectmap__
        self.resource = create_dummy_resource(parent=context)
        self.resource2 = create_dummy_resource(parent=context)

    def _make_one(self, resource, **kwargs):
        from adhocracy.graph import Graph
        graph = Graph(None)
        graph._objectmap = self.objectmap
        return Graph.get_references(graph, resource, **kwargs)

    def test_no_reference(self):
        result = self._make_one(self.resource)
        assert list(result) == []

    def test_no_sheetreferences(self):
        self.objectmap.connect(self.resource, self.resource, 'NoSheetReference')
        result = self._make_one(self.resource)
        assert list(result) == []

    def test_sheetreferences(self):
        self.objectmap.connect(self.resource, self.resource2, SheetToSheet)

        result = self._make_one(self.resource)

        source, isheet, field, target = result.__next__()
        assert source == self.resource
        assert isheet == SheetReference.getTaggedValue('source_isheet')
        assert field == SheetReference.getTaggedValue('source_isheet_field')
        assert target == self.resource2

    def test_sheetreferences_with_base_reftype(self):
        class ASheetReferenceType(SheetReference):
            pass

        self.objectmap.connect(self.resource, self.resource,
                               SheetReference)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)

        result = self._make_one(self.resource, base_reftype=ASheetReferenceType)
        assert len(list(result)) == 1

    def test_sheetreferences_with_base_isheet(self):
        class IASheet(ISheet):
            pass

        class ASheetReferenceType(SheetToSheet):
            source_isheet = IASheet

        self.objectmap.connect(self.resource, self.resource,
                               SheetReference)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)

        result = self._make_one(self.resource, base_isheet=IASheet)
        assert len(list(result)) == 1


class GraphGetBackReferencesUnitTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap_method = ObjectMap.sources
        self.objectmap = context.__objectmap__
        self.resource = create_dummy_resource(parent=context)
        self.resource2 = create_dummy_resource(parent=context)

    def _make_one(self, resource, **kwargs):
        from adhocracy.graph import Graph
        graph = Graph(None)
        graph._objectmap = self.objectmap
        return Graph.get_back_references(graph, resource, **kwargs)

    def test_no_reference(self):
        result = self._make_one(self.resource)
        assert list(result) == []

    def test_no_sheetreferences(self):
        self.objectmap.connect(self.resource, self.resource, 'NoSheetReference')
        result = self._make_one(self.resource)
        assert list(result) == []

    def test_sheetreferences(self):
        self.objectmap.connect(self.resource, self.resource2,
                               SheetToSheet)

        result = self._make_one(self.resource2)

        source, isheet, field, target = result.__next__()
        assert source == self.resource
        assert isheet == SheetToSheet.getTaggedValue('source_isheet')
        assert field == SheetToSheet.getTaggedValue('source_isheet_field')
        assert target == self.resource2

    def test_sheetreferences_and_base_reftype(self):
        from adhocracy.interfaces import SheetReference

        class ASheetReferenceType(SheetReference):
            pass

        self.objectmap.connect(self.resource, self.resource,
                               SheetReference)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)

        result = self._make_one(self.resource, base_reftype=ASheetReferenceType)
        assert len(list(result)) == 1

    def test_sheetreferences_and_base_isheet(self):
        class IASheet(ISheet):
            pass

        class ASheetReferenceType(SheetToSheet):
            source_isheet = IASheet

        self.objectmap.connect(self.resource, self.resource,
                               SheetReference)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)

        result = self._make_one(self.resource, base_isheet=IASheet)
        assert len(list(result)) == 1


class GraphGetBackReferencesForIsheetUnitTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap = context.__objectmap__
        self.source = create_dummy_resource(parent=context)
        self.target = create_dummy_resource(parent=context)

    def _make_one(self, context, isheet):
        from adhocracy.graph import Graph
        graph = Graph(None)
        graph._objectmap = self.objectmap
        return Graph.get_back_references_for_isheet(graph, context, isheet)

    def test_with_isheet_but_no_rerferences(self):
        class IASheet(ISheet):
            taggedValue('field:name', None)
        result = self._make_one(self.target, IASheet)
        assert result == {}

    def test_with_isheet(self):
        class IASheet(ISheet):
            taggedValue('field:name', None)

        class ASheetToSheet(SheetToSheet):
            source_isheet = IASheet
            source_isheet_field = 'name'
        self.objectmap.connect(self.source, self.target, ASheetToSheet)

        result = self._make_one(self.target, IASheet)

        assert result == {'name': [self.source]}

    def test_with_isheet_that_has_subclass(self):
        from adhocracy.interfaces import SheetToSheet
        from adhocracy.interfaces import ISheet
        self.objectmap.connect(self.source, self.target,
                               SheetToSheet)

        class IASheet(ISheet):
            taggedValue('field:name', None)

        class ASheetReferenceType(SheetToSheet):
            source_isheet = IASheet
            source_isheet_field = 'name'

        class IABSheet(IASheet):
            taggedValue('field:name', None)

        class ABSheetReferenceType(SheetToSheet):
            source_isheet = IABSheet
            source_isheet_field = 'name'

        self.objectmap.connect(self.source, self.target, ASheetReferenceType)
        self.objectmap.connect(self.source, self.target, ABSheetReferenceType)

        result = self._make_one(self.target, IASheet)
        assert result == {'name': [self.source, self.source]}

    def test_with_isheet_that_has_subclass_with_extra_field(self):
        from adhocracy.interfaces import SheetToSheet
        from adhocracy.interfaces import ISheet

        class IASheet(ISheet):
            taggedValue('field:name', None)

        class ASheetReferenceType(SheetToSheet):
            source_isheet = IASheet
            source_isheet_field = 'name'

        class IABSheet(IASheet):
            taggedValue('field:othername', None)

        class ABSheetReferenceType(SheetToSheet):
            source_isheet = IABSheet
            source_isheet_field = 'othername'

        self.objectmap.connect(self.source, self.target, SheetReference)
        self.objectmap.connect(self.source, self.target, ASheetReferenceType)
        self.objectmap.connect(self.source, self.target, ABSheetReferenceType)

        result = self._make_one(self.target, IASheet)
        assert result == {'name': [self.source], 'othername': [self.source]}


class GraphGetReferencesForIsheetUnitTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap = context.__objectmap__
        self.source = create_dummy_resource(parent=context)
        self.target = create_dummy_resource(parent=context)

    def _make_one(self, context, isheet):
        from adhocracy.graph import Graph
        graph = Graph(None)
        graph._objectmap = self.objectmap
        return Graph.get_references_for_isheet(graph, context, isheet)

    def test_with_isheet(self):
        class IASheet(ISheet):
            taggedValue('field:name', None)

        class ASheetToSheet(SheetToSheet):
            source_isheet = IASheet
            source_isheet_field = 'name'
        self.objectmap.connect(self.source, self.target, ASheetToSheet)

        result = self._make_one(self.source, IASheet)

        assert result == {'name': [self.target]}


class GetFollowsUnitTest(unittest.TestCase):

    @patch('adhocracy.graph.Graph')
    def setUp(self, dummy_graph=None):
        self.context = testing.DummyResource()
        self.graph = dummy_graph.return_value

    def _make_one(self, context):
        from adhocracy.graph import Graph
        graph = self.graph
        return Graph.get_follows(graph, context)

    def test_precssors(self):
        old = testing.DummyResource()
        self.graph.get_references.return_value = iter([(None, None, None, old)])
        follows = list(self._make_one(self.context))
        assert self.graph.get_references.call_args[0][0] == self.context
        assert self.graph.get_references.call_args[1]['base_reftype']\
            == NewVersionToOldVersion
        assert follows == [old]

    def test_no_precssors(self):
        self.graph.get_references.return_value = iter([])
        follows = list(self._make_one(self.context))
        assert follows == []


class GetFollowedByUnitTest(unittest.TestCase):

    @patch('adhocracy.graph.Graph')
    def setUp(self, dummy_graph=None):
        self.context = create_dummy_resource()
        self.graph = dummy_graph.return_value

    def _make_one(self, context):
        from adhocracy.graph import Graph
        graph = self.graph
        return Graph.get_followed_by(graph, context)

    def test_sucessors(self):
        new = testing.DummyResource()
        self.graph.get_back_references.return_value = iter([(new, None, None,
                                                             None)])
        follows_by = list(self._make_one(self.context))
        assert self.graph.get_back_references.call_args[0][0] == self.context
        assert self.graph.get_back_references.call_args[1]['base_reftype'] ==\
            NewVersionToOldVersion
        assert follows_by == [new]

    def test_no_sucessors(self):
        new = testing.DummyResource()
        self.graph.get_back_references.return_value = iter([])
        follows_by = list(self._make_one(self.context))
        assert follows_by == []


class GraphIsInSubtreeUnitTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.context = context
        self.child = create_dummy_resource(parent=context)
        self.objectmap = context.__objectmap__

    def _make_one(self, descendant, ancestors):
        from adhocracy.graph import Graph
        graph = Graph(None)
        graph._objectmap = self.objectmap
        return Graph.is_in_subtree(graph, descendant, ancestors)

    def test_with_no_ancestors(self):
        """False if ancestors is an empty list."""
        result = self._make_one(self.child, [])
        assert result is False

    def test_of_itself(self):
        """True if both are the same resource."""
        result = self._make_one(self.child, [self.child])
        assert result is True

    def test_direct_link(self):
        """True if direct SheetToSheet link from ancestor to
        descendent.
        """
        root = create_dummy_resource(parent=self.context)
        element = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(root, element, SheetToSheet)
        result = self._make_one(element, [root])
        assert result is True
        # Inverse relation should NOT be found
        result = self._make_one(root, [element])
        assert result is False

    def test_direct_follows_link(self):
        """False if direct NewVersionToOldVersion link from ancestor to
        descendent.
        """
        other_version = create_dummy_resource(parent=self.context)
        old_version = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(other_version, old_version, NewVersionToOldVersion)
        result = self._make_one(old_version, [other_version])
        assert result is False
        # Inverse relation should not be found either
        result = self._make_one(other_version, [old_version])
        assert result is False

    def test_indirect_link(self):
        """True if two-level SheetToSheet link from ancestor to
        descendent.
        """
        grandma = create_dummy_resource(parent=self.context)
        dad = create_dummy_resource(parent=self.context)
        daugher = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(grandma, dad, SheetToSheet)
        om.connect(dad, daugher, SheetToSheet)
        result = self._make_one(daugher, [grandma])
        assert result is True
        # Inverse relation should NOT be found
        result = self._make_one(grandma, [daugher])
        assert result is False

    def test_indirect_follows_link(self):
        """True if two-level link from ancestor to descendent that includes a
        follows relation.
        """
        dad = create_dummy_resource(parent=self.context)
        daugher = create_dummy_resource(parent=self.context)
        step_son = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(dad, daugher, SheetToSheet)
        om.connect(step_son, daugher, NewVersionToOldVersion)
        result = self._make_one(step_son, [dad])
        assert result is False
        # Inverse relation should not be found either
        result = self._make_one(dad, [step_son])
        assert result is False

    def test_ancestor_list_has_multiple_elements(self):
        """True if ancestors is a two-element list and one of them is the right
        one.
        """
        root = create_dummy_resource(parent=self.context)
        not_root = create_dummy_resource(parent=self.context)
        element = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(root, element, SheetToSheet)
        result = self._make_one(element, [root, not_root])
        assert result is True
        result = self._make_one(element, [not_root, root])
        assert result is True
