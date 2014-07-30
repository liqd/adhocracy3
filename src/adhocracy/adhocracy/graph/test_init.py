from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark

from zope.interface import taggedValue
from zope.interface import Interface
from adhocracy.interfaces import SheetReference
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import NewVersionToOldVersion


def create_dummy_resources(parent=None, count=1):
    """Create dummy resources and add it to the parent objectmap."""
    from pyramid.traversal import resource_path_tuple
    resources = ()
    for x in range(count):
        resource = testing.DummyResource(__parent__=parent)
        oid = parent.__objectmap__.new_objectid()
        resource.__oid__ = oid
        resource.__name__ = str(oid)
        path = resource_path_tuple(resource)
        parent[resource.__name__] = resource
        parent.__objectmap__.add(resource, path)
        resources = resources + (resource,)
    return resources[0] if count == 1 else resources


@fixture()
def objectmap():
    from substanced.objectmap import ObjectMap
    context = testing.DummyResource()
    context.__objectmap__ = ObjectMap(context)
    return context.__objectmap__


@fixture()
def context(objectmap):
    context = objectmap.root
    context.__objectmap__ = objectmap
    return context


class TestGraph:

    def _make_one(self, context):
        from adhocracy.graph import Graph
        return Graph(context)

    def test_create(self, context):
        from persistent import Persistent
        graph = self._make_one(context)
        assert issubclass(graph.__class__, Persistent)
        assert graph._objectmap is context.__objectmap__

    def test_create_with_missing_objectmap(self):
        graph = self._make_one(None)
        assert graph._objectmap is None


class TestGraphGetReftypes:

    def _call_fut(self, mock_objectmap, **kwargs):
        from adhocracy.graph import Graph
        context = testing.DummyResource()
        context.__objectmap__ = mock_objectmap
        graph = Graph(context=context)
        return Graph.get_reftypes(graph, **kwargs)

    def test_no_objectmap(self, mock_objectmap):
        assert list(self._call_fut(mock_objectmap)) == []

    def test_no_reftpyes(self, mock_objectmap):
        mock_objectmap.get_reftypes.return_value = []
        assert list(self._call_fut(mock_objectmap)) == []

    def test_one_wrong_str_reftype(self, mock_objectmap):
        mock_objectmap.get_reftypes.return_value = ["NoneSheetToSheet"]
        assert list(self._call_fut(mock_objectmap)) == []

    def test_one_wrong_no_sheetreference_reftype(self, mock_objectmap):
        mock_objectmap.get_reftypes.return_value = [Interface]
        assert list(self._call_fut(mock_objectmap)) == []

    def test_one_wrong_source_isheet(self, mock_objectmap):
        class SubSheetToSheet(SheetToSheet):
            source_isheet = Interface
        mock_objectmap.get_reftypes.return_value = [SubSheetToSheet]
        assert list(self._call_fut(mock_objectmap)) == []

    def test_one_valid_reftype(self, mock_objectmap):
        mock_objectmap.get_reftypes.return_value = [SheetToSheet]
        reftypes = list(self._call_fut(mock_objectmap))
        assert reftypes[0] == (ISheet, '', SheetToSheet)

    def test_with_base_reftype(self, mock_objectmap):
        class SubSheetToSheet(SheetToSheet):
            pass
        mock_objectmap.get_reftypes.return_value = [SubSheetToSheet,
                                                    SheetToSheet]
        reftypes = list(self._call_fut(mock_objectmap, base_reftype=SubSheetToSheet))
        assert len(reftypes) == 1

    def test_with_base_reftype_that_has_subclass(self, mock_objectmap):
        class SubSheetToSheet(SheetToSheet):
            pass
        mock_objectmap.get_reftypes.return_value = [SubSheetToSheet,
                                               SheetToSheet]
        reftypes = list(self._call_fut(mock_objectmap, base_reftype=SheetToSheet))
        assert len(reftypes) == 2

    def test_with_base_isheet(self, mock_objectmap):
        class ISheetA(ISheet):
            pass

        class SubSheetToSheet(SheetToSheet):
            source_isheet = ISheetA

        mock_objectmap.get_reftypes.return_value = [SubSheetToSheet,
                                                    SheetToSheet]
        reftypes = list(self._call_fut(mock_objectmap, base_isheet=ISheetA))
        assert len(reftypes) == 1

    def test_with_base_isheet_that_has_subclass(self, mock_objectmap):
        class ISheetA(ISheet):
            pass

        class SubSheetToSheet(SheetToSheet):
            source_isheet = ISheetA

        mock_objectmap.get_reftypes.return_value = [SubSheetToSheet,
                                                    SheetToSheet]
        reftypes = list(self._call_fut(mock_objectmap, base_isheet=ISheet))
        assert len(reftypes) == 2


class TestGraphSetReferences:

    def _call_fut(self, objectmap, *args):
        from adhocracy.graph import Graph
        graph = Graph(objectmap.root)
        return Graph.set_references(graph, *args)

    def test_reftype_not_sheetreferencetype(self, context, objectmap):
        from substanced.interfaces import ReferenceType
        source = create_dummy_resources(parent=context)
        with raises(AssertionError):
            self._call_fut(objectmap, source, [], ReferenceType)

    def test_targets_empty_list(self, context, objectmap):
        source = create_dummy_resources(parent=context)
        self._call_fut(objectmap, source, [], SheetReference)
        references = objectmap.targetids(source, SheetReference)
        assert list(references) == []

    def test_targets_list(self, context, objectmap):
        source, target = create_dummy_resources(parent=context, count=2)
        self._call_fut(objectmap, source, [target], SheetReference)
        references = objectmap.targetids(source, SheetReference)
        assert list(references) == [target.__oid__]

    def test_targets_list_ordered(self, context, objectmap):
        source, target, target1 = create_dummy_resources(parent=context, count=3)
        self._call_fut(objectmap, source, [target, target1], SheetReference)
        self._call_fut(objectmap, source, [target1, target], SheetReference)

        references = objectmap.targetids(source, SheetReference)
        assert list(references) == [target1.__oid__, target.__oid__]

    def test_targets_list_duplicated_targets(self, context, objectmap):
        """Duplication targets are not possible with substanced.objectmap."""
        source, target = create_dummy_resources(parent=context, count=2)
        self._call_fut(objectmap, source, [target, target], SheetReference)
        references = objectmap.targetids(source, SheetReference)
        assert list(references) == [target.__oid__]

    def test_targets_list_with_some_removed(self, context, objectmap):
        source, target, target1 = create_dummy_resources(parent=context, count=3)
        self._call_fut(objectmap, source, [target, target1], SheetReference)
        self._call_fut(objectmap, source, [target], SheetReference)

        references = objectmap.targetids(source, SheetReference)
        assert list(references) == [target.__oid__]

    def test_targets_set(self, context, objectmap):
        source, target = create_dummy_resources(parent=context, count=2)
        self._call_fut(objectmap, source, {target}, SheetReference)
        references = objectmap.targetids(source, SheetReference)
        assert list(references) == [target.__oid__]

    def test_targets_set_duplicated_targets(self, context, objectmap):
        source, target = create_dummy_resources(parent=context, count=2)
        self._call_fut(objectmap, source, {target, target}, SheetReference)
        references = objectmap.targetids(source, SheetReference)
        assert list(references) == [target.__oid__]

    def test_targets_set_with_some_removed(self, context, objectmap):
        source, target, target1 = create_dummy_resources(parent=context, count=3)
        self._call_fut(objectmap, source, {target, target1}, SheetReference)
        self._call_fut(objectmap, source, {target}, SheetReference)
        references = objectmap.targetids(source, SheetReference)
        assert list(references) == [target.__oid__]


class TestGraphGetReferences:

    def _call_fut(self, objectmap, resource, **kwargs):
        from adhocracy.graph import Graph
        graph = Graph(objectmap.root)
        return Graph.get_references(graph, resource, **kwargs)

    def test_no_reference(self, objectmap):
        resource = testing.DummyResource()
        result = self._call_fut(objectmap, resource)
        assert list(result) == []

    def test_no_sheetreferences(self, context, objectmap):
        resource = create_dummy_resources(parent=context)
        objectmap.connect(resource, resource, 'NoSheetReference')
        result = self._call_fut(objectmap, resource)
        assert list(result) == []

    def test_sheetreferences(self, context, objectmap):
        resource, resource2 = create_dummy_resources(parent=context, count=2)
        objectmap.connect(resource, resource2, SheetToSheet)

        result = self._call_fut(objectmap, resource)

        source, isheet, field, target = result.__next__()
        assert source == resource
        assert isheet == SheetReference.getTaggedValue('source_isheet')
        assert field == SheetReference.getTaggedValue('source_isheet_field')
        assert target == resource2

    def test_sheetreferences_with_base_reftype(self, context, objectmap):
        resource = create_dummy_resources(parent=context)
        class ASheetReferenceType(SheetReference):
            pass
        objectmap.connect(resource, resource, SheetReference)
        objectmap.connect(resource, resource, ASheetReferenceType)

        result = self._call_fut(objectmap, resource, base_reftype=ASheetReferenceType)
        assert len(list(result)) == 1

    def test_sheetreferences_with_base_isheet(self, context, objectmap):
        resource = create_dummy_resources(parent=context)
        class IASheet(ISheet):
            pass
        class ASheetReferenceType(SheetToSheet):
            source_isheet = IASheet
        objectmap.connect(resource, resource, SheetReference)
        objectmap.connect(resource, resource, ASheetReferenceType)

        result = self._call_fut(objectmap, resource, base_isheet=IASheet)
        assert len(list(result)) == 1


class TestGraphGetBackReferences:

    def _call_fut(self, objectmap, resource, **kwargs):
        from adhocracy.graph import Graph
        graph = Graph(objectmap.root)
        return Graph.get_back_references(graph, resource, **kwargs)

    def test_no_reference(self, context, objectmap):
        resource = create_dummy_resources(parent=context)
        result = self._call_fut(objectmap, resource)
        assert list(result) == []

    def test_no_sheetreferences(self, context, objectmap):
        resource = create_dummy_resources(parent=context)
        objectmap.connect(resource, resource, 'NoSheetReference')
        result = self._call_fut(objectmap, resource)
        assert list(result) == []

    def test_sheetreferences(self, context, objectmap):
        resource, resource2 = create_dummy_resources(parent=context, count=2)
        objectmap.connect(resource, resource2, SheetToSheet)

        result = self._call_fut(objectmap, resource2)

        source, isheet, field, target = result.__next__()
        assert source == resource
        assert isheet == SheetToSheet.getTaggedValue('source_isheet')
        assert field == SheetToSheet.getTaggedValue('source_isheet_field')
        assert target == resource2

    def test_sheetreferences_and_base_reftype(self, context, objectmap):
        resource = create_dummy_resources(parent=context)
        class ASheetReferenceType(SheetReference):
            pass
        objectmap.connect(resource, resource, SheetReference)
        objectmap.connect(resource, resource, ASheetReferenceType)

        result = self._call_fut(objectmap, resource, base_reftype=ASheetReferenceType)

        assert len(list(result)) == 1

    def test_sheetreferences_and_base_isheet(self, context, objectmap):
        resource = create_dummy_resources(parent=context)
        class IASheet(ISheet):
            pass
        class ASheetReferenceType(SheetToSheet):
            source_isheet = IASheet
        objectmap.connect(resource, resource, SheetReference)
        objectmap.connect(resource, resource, ASheetReferenceType)

        result = self._call_fut(objectmap, resource, base_isheet=IASheet)

        assert len(list(result)) == 1


class TestGraphGetBackReferencesForIsheet:

    def _call_fut(self, objectmap, target, isheet):
        from adhocracy.graph import Graph
        graph = Graph(objectmap.root)
        return Graph.get_back_references_for_isheet(graph, target, isheet)

    def test_with_isheet_but_no_rerferences(self, context, objectmap):
        target = create_dummy_resources(parent=context)
        class IASheet(ISheet):
            taggedValue('field:name', None)
        result = self._call_fut(objectmap, target, IASheet)
        assert result == {}

    def test_with_isheet(self, context, objectmap):
        source, target = create_dummy_resources(parent=context, count=2)
        class IASheet(ISheet):
            taggedValue('field:name', None)
        class ASheetToSheet(SheetToSheet):
            source_isheet = IASheet
            source_isheet_field = 'name'
        objectmap.connect(source, target, ASheetToSheet)

        result = self._call_fut(objectmap, target, IASheet)

        assert result == {'name': [source]}

    def test_with_isheet_that_has_subclass(self, context, objectmap):
        from adhocracy.interfaces import SheetToSheet
        from adhocracy.interfaces import ISheet
        source, target = create_dummy_resources(parent=context, count=2)
        objectmap.connect(source, target, SheetToSheet)
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
        objectmap.connect(source, target, ASheetReferenceType)
        objectmap.connect(source, target, ABSheetReferenceType)

        result = self._call_fut(objectmap, target, IASheet)

        assert result == {'name': [source, source]}

    def test_with_isheet_that_has_subclass_with_extra_field(self, context, objectmap):
        from adhocracy.interfaces import SheetToSheet
        from adhocracy.interfaces import ISheet
        source, target = create_dummy_resources(parent=context, count=2)
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
        objectmap.connect(source, target, SheetReference)
        objectmap.connect(source, target, ASheetReferenceType)
        objectmap.connect(source, target, ABSheetReferenceType)

        result = self._call_fut(objectmap, target, IASheet)

        assert result == {'name': [source], 'othername': [source]}


class TestGraphGetReferencesForIsheet:

    @fixture()
    def context(self, context):
        from substanced.objectmap import ObjectMap
        context.__objectmap__ = ObjectMap(context)
        return context

    def _call_fut(self, context, source, isheet):
        from adhocracy.graph import Graph
        graph = Graph(context)
        return Graph.get_references_for_isheet(graph, source, isheet)

    def test_with_isheet(self, context):
        source, target = create_dummy_resources(parent=context, count=2)
        class IASheet(ISheet):
            taggedValue('field:name', None)
        class ASheetToSheet(SheetToSheet):
            source_isheet = IASheet
            source_isheet_field = 'name'
        context.__objectmap__.connect(source, target, ASheetToSheet)
        result = self._call_fut(context, source, IASheet)
        assert result == {'name': [target]}


class TestGetFollows:

    def _make_one(self, mock_graph, context):
        from adhocracy.graph import Graph
        return Graph.get_follows(mock_graph, context)

    def test_predecessor(self, mock_graph, context):
        from adhocracy.graph import Reference
        old = testing.DummyResource()
        mock_graph.get_references.return_value = iter(
            [Reference(None, None, None, old)])
        follows = list(self._make_one(mock_graph, context))
        assert mock_graph.get_references.call_args[0][0] == context
        assert mock_graph.get_references.call_args[1]['base_reftype']\
            == NewVersionToOldVersion
        assert follows == [old]

    def test_no_predecessor(self, mock_graph, context):
        mock_graph.get_references.return_value = iter([])
        follows = list(self._make_one(mock_graph, context))
        assert follows == []


class TestGetFollowedBy:

    def _make_one(self, mock_graph, context):
        from adhocracy.graph import Graph
        return Graph.get_followed_by(mock_graph, context)

    def test_sucessors(self, mock_graph, context):
        from adhocracy.graph import Reference
        new = testing.DummyResource()
        mock_graph.get_back_references.return_value = iter(
            [Reference(new, None, None, None)])
        follows_by = list(self._make_one(mock_graph, context))
        assert mock_graph.get_back_references.call_args[0][0] == context
        assert mock_graph.get_back_references.call_args[1]['base_reftype'] ==\
            NewVersionToOldVersion
        assert follows_by == [new]

    def test_no_sucessors(self, mock_graph, context):
        mock_graph.get_back_references.return_value = iter([])
        follows_by = list(self._make_one(mock_graph, context))
        assert follows_by == []


@mark.usefixtures('setup')
class TestGraphIsInSubtree:

    @fixture()
    def setup(self, context):
        from substanced.objectmap import ObjectMap
        context.__objectmap__ = ObjectMap(context)
        self.context = context
        self.child = create_dummy_resources(parent=context)
        context.__objectmap = context.__objectmap__

    def _call_fut(self, descendant, ancestors):
        from adhocracy.graph import Graph
        context = testing.DummyResource(__objectmap__=self.context.__objectmap)
        graph = Graph(context)
        return Graph.is_in_subtree(graph, descendant, ancestors)

    def test_with_no_ancestors(self):
        """False if ancestors is an empty list."""
        result = self._call_fut(self.child, [])
        assert result is False

    def test_of_itself(self):
        """True if both are the same resource."""
        result = self._call_fut(self.child, [self.child])
        assert result is True

    def test_direct_link(self):
        """True if direct SheetToSheet link from ancestor to
        descendent.
        """
        root = create_dummy_resources(parent=self.context)
        element = create_dummy_resources(parent=self.context)
        om = self.context.__objectmap__
        om.connect(root, element, SheetToSheet)
        result = self._call_fut(element, [root])
        assert result is True
        # Inverse relation should NOT be found
        result = self._call_fut(root, [element])
        assert result is False

    def test_direct_follows_link(self):
        """False if direct NewVersionToOldVersion link from ancestor to
        descendent.
        """
        other_version = create_dummy_resources(parent=self.context)
        old_version = create_dummy_resources(parent=self.context)
        om = self.context.__objectmap__
        om.connect(other_version, old_version, NewVersionToOldVersion)
        result = self._call_fut(old_version, [other_version])
        assert result is False
        # Inverse relation should not be found either
        result = self._call_fut(other_version, [old_version])
        assert result is False

    def test_indirect_link(self):
        """True if two-level SheetToSheet link from ancestor to
        descendent.
        """
        grandma = create_dummy_resources(parent=self.context)
        dad = create_dummy_resources(parent=self.context)
        daugher = create_dummy_resources(parent=self.context)
        om = self.context.__objectmap__
        om.connect(grandma, dad, SheetToSheet)
        om.connect(dad, daugher, SheetToSheet)
        result = self._call_fut(daugher, [grandma])
        assert result is True
        # Inverse relation should NOT be found
        result = self._call_fut(grandma, [daugher])
        assert result is False

    def test_indirect_follows_link(self):
        """True if two-level link from ancestor to descendent that includes a
        follows relation.
        """
        dad = create_dummy_resources(parent=self.context)
        daugher = create_dummy_resources(parent=self.context)
        step_son = create_dummy_resources(parent=self.context)
        om = self.context.__objectmap__
        om.connect(dad, daugher, SheetToSheet)
        om.connect(step_son, daugher, NewVersionToOldVersion)
        result = self._call_fut(step_son, [dad])
        assert result is False
        # Inverse relation should not be found either
        result = self._call_fut(dad, [step_son])
        assert result is False

    def test_ancestor_list_has_multiple_elements(self):
        """True if ancestors is a two-element list and one of them is the right
        one.
        """
        root = create_dummy_resources(parent=self.context)
        not_root = create_dummy_resources(parent=self.context)
        element = create_dummy_resources(parent=self.context)
        om = self.context.__objectmap__
        om.connect(root, element, SheetToSheet)
        result = self._call_fut(element, [root, not_root])
        assert result is True
        result = self._call_fut(element, [not_root, root])
        assert result is True


def test_includeme_register_graph(config, context):
    from adhocracy.graph import Graph
    config.include('adhocracy.registry')
    config.include('adhocracy.graph')
    graph = config.registry.content.create('Graph', context)
    assert isinstance(graph, Graph)
