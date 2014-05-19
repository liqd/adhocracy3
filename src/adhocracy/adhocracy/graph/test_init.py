import unittest

from mock import patch
from pyramid import testing
from zope.interface import taggedValue
from zope.interface import Interface
import pytest

from adhocracy.interfaces import IResource
from adhocracy.interfaces import SheetReferenceType
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

class GetReftypesUnitTest(unittest.TestCase):

    def _make_one(self, objectmap, **kwargs):
        from adhocracy.graph import _get_reftypes
        return _get_reftypes(objectmap, **kwargs)

    @patch('substanced.objectmap.ObjectMap', autospec=True)
    def setUp(self, dummy_objectmap=None):
        self.objectmap = dummy_objectmap.return_value

    def test_empty_objectmap(self):
        om = self.objectmap
        om.get_reftypes.return_value = []
        result = list(self._make_one(om))
        assert result == []

    def test_one_wrong_reftype(self):
        om = self.objectmap
        om.get_reftypes.return_value = ["NoneSheetToSheet"]
        result = list(self._make_one(om))
        assert result == []

    def test_one_wrong_isheet(self):
        class IReftype(Interface):
            taggedValue('source_isheet', Interface)
        om = self.objectmap
        om.get_reftypes.return_value = [IReftype]

        result = list(self._make_one(om))

        assert result == []

    def test_with_valid_reftype(self):
        om = self.objectmap
        om.get_reftypes.return_value = [SheetToSheet]
        result = list(self._make_one(om))
        assert len(result) == 1
        assert result[0] == (ISheet, '', SheetToSheet)

    def test_with_valid_reftype_and_base_reftype(self):
        class IOtherReferenceType(SheetToSheet):
            pass
        om = self.objectmap
        om.get_reftypes.return_value = [IOtherReferenceType,
                                        SheetToSheet]
        result = list(self._make_one(om, base_reftype=IOtherReferenceType))
        assert len(result) == 1
        assert IOtherReferenceType == result[0][2]

    def test_with_valid_reftype_and_base_reftype_thas_has_subclass(self):
        class IOtherReferenceType(SheetToSheet):
            pass
        om = self.objectmap
        om.get_reftypes.return_value = [IOtherReferenceType,
                                        SheetToSheet]
        result = list(self._make_one(om, base_reftype=SheetToSheet))
        assert len(result) == 2

    def test_with_valid_reftype_and_base_isheet(self):
        class ISheetA(ISheet):
            pass

        class IOtherReferenceType(SheetToSheet):
            pass
        IOtherReferenceType.setTaggedValue('source_isheet', ISheetA)
        om = self.objectmap
        om.get_reftypes.return_value = [IOtherReferenceType,
                                        SheetToSheet]
        result = list(self._make_one(om, base_isheet=ISheetA))
        assert len(result) == 1

    def test_with_valid_reftype_and_base_isheet_that_has_subclass(self):
        class ISheetA(ISheet):
            pass

        class IOtherReferenceType(SheetToSheet):
            taggedValue('source_isheet', ISheetA)
        om = self.objectmap
        om.get_reftypes.return_value = [IOtherReferenceType,
                                        SheetToSheet]
        result = list(self._make_one(om, base_isheet=ISheet))
        assert len(result) == 2


class SetReferencesUnitTest(unittest.TestCase):

    def _make_one(self, *args):
        from adhocracy.graph import set_references
        return set_references(*args)

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.source = create_dummy_resource(parent=context)
        self.target = create_dummy_resource(parent=context)
        self.target1 = create_dummy_resource(parent=context)
        self.target2 = create_dummy_resource(parent=context)
        self.objectmap = context.__objectmap__

    def test_targets_not_iteratable(self):
        with pytest.raises(AssertionError):
            self._make_one(self.source, None, SheetReferenceType)

    def test_reftype_not_sheetreferencetype(self):
        from substanced.interfaces import ReferenceType
        with pytest.raises(AssertionError):
            self._make_one(self.source, [], ReferenceType)

    def test_resource_no_object(self):
        with pytest.raises(AssertionError):
            self._make_one(None, [], SheetReferenceType)

    def test_targets_empty_list(self):
        self._make_one(self.source, [], SheetReferenceType)
        references = self.objectmap.targetids(self.source, SheetReferenceType)
        wanted_refs = []
        assert wanted_refs == list(references)

    def test_targets_list(self):
        targets = [self.target]
        self._make_one(self.source, targets, SheetReferenceType)
        references = self.objectmap.targetids(self.source, SheetReferenceType)
        wanted_references = [self.target.__oid__]
        assert wanted_references == list(references)

    def test_targets_list_ordered(self):
        targets = [self.target, self.target1, self.target2]
        self._make_one(self.source, targets, SheetReferenceType)
        targets_reverse = [self.target2, self.target1, self.target]
        self._make_one(self.source, targets_reverse, SheetReferenceType)

        references = self.objectmap.targetids(self.source, SheetReferenceType)
        wanted_references = [x.__oid__ for x in targets_reverse]
        assert wanted_references == list(references)

    def test_targets_list_duplicated_targets(self):
        """Duplication targets are not possible with substanced.objectmap."""
        targets = [self.target, self.target]
        self._make_one(self.source, targets, SheetReferenceType)
        references = self.objectmap.targetids(self.source, SheetReferenceType)
        wanted_references = [self.target.__oid__]
        assert wanted_references == list(references)

    def test_targets_list_with_some_removed(self):
        targets = [self.target, self.target1, self.target2]
        self._make_one(self.source, targets, SheetReferenceType)
        targets_some_removed = [self.target]
        self._make_one(self.source, targets_some_removed, SheetReferenceType)

        references = self.objectmap.targetids(self.source, SheetReferenceType)
        wanted_references = [x.__oid__ for x in targets_some_removed]
        assert wanted_references == list(references)

    def test_targets_set(self):
        targets = {self.target}
        self._make_one(self.source, targets, SheetReferenceType)
        references = self.objectmap.targetids(self.source, SheetReferenceType)
        wanted_references = [self.target.__oid__]
        assert wanted_references == list(references)

    def test_targets_set_duplicated_targets(self):
        targets = {self.target, self.target}
        self._make_one(self.source, targets, SheetReferenceType)
        references = self.objectmap.targetids(self.source, SheetReferenceType)
        wanted_references = [self.target.__oid__]
        assert wanted_references == list(references)

    def test_targets_set_with_some_removed(self):
        targets = {self.target, self.target1, self.target2}
        self._make_one(self.source, targets, SheetReferenceType)
        targets_some_removed = {self.target}
        self._make_one(self.source, targets_some_removed, SheetReferenceType)

        references = self.objectmap.targetids(self.source, SheetReferenceType)
        wanted_references = [x.__oid__ for x in targets_some_removed]
        assert wanted_references == list(references)


class GetReferencesUnitTest(unittest.TestCase):

    def _make_one(self, resource, **kwargs):
        from adhocracy.graph import get_references
        return get_references(resource, **kwargs)

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap_method = ObjectMap.sources
        self.objectmap = context.__objectmap__
        self.resource = create_dummy_resource(parent=context)
        self.resource2 = create_dummy_resource(parent=context)

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
        assert isheet == SheetReferenceType.getTaggedValue('source_isheet')
        assert field == SheetReferenceType.getTaggedValue('source_isheet_field')
        assert target == self.resource2

    def test_sheetreferences_with_base_reftype(self):
        class ASheetReferenceType(SheetReferenceType):
            pass

        self.objectmap.connect(self.resource, self.resource,
                               SheetReferenceType)
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
                               SheetReferenceType)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)

        result = self._make_one(self.resource, base_isheet=IASheet)
        assert len(list(result)) == 1


class GetBackReferencesUnitTest(unittest.TestCase):

    def _make_one(self, resource, **kwargs):
        from adhocracy.graph import get_back_references
        return get_back_references(resource, **kwargs)

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap_method = ObjectMap.sources
        self.objectmap = context.__objectmap__
        self.resource = create_dummy_resource(parent=context)
        self.resource2 = create_dummy_resource(parent=context)

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
        from adhocracy.interfaces import SheetReferenceType

        class ASheetReferenceType(SheetReferenceType):
            pass

        self.objectmap.connect(self.resource, self.resource,
                               SheetReferenceType)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)

        result = self._make_one(self.resource, base_reftype=ASheetReferenceType)
        assert len(list(result)) == 1

    def test_sheetreferences_and_base_isheet(self):
        class IASheet(ISheet):
            pass

        class ASheetReferenceType(SheetReferenceType):
            source_isheet = IASheet

        self.objectmap.connect(self.resource, self.resource,
                               SheetReferenceType)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)

        result = self._make_one(self.resource, base_isheet=IASheet)
        assert len(list(result)) == 1


class GetBackReferencesForIsheetUnitTest(unittest.TestCase):

    def _make_one(self, context, isheet):
        from adhocracy.graph import get_back_references_for_isheet
        return get_back_references_for_isheet(context, isheet)

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap = context.__objectmap__
        self.source = create_dummy_resource(parent=context)
        self.target = create_dummy_resource(parent=context)

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
        from adhocracy.interfaces import SheetReferenceType
        from adhocracy.interfaces import ISheet
        self.objectmap.connect(self.source, self.target,
                               SheetReferenceType)

        class IASheet(ISheet):
            taggedValue('field:name', None)

        class ASheetReferenceType(SheetReferenceType):
            source_isheet = IASheet
            source_isheet_field = 'name'

        class IABSheet(IASheet):
            taggedValue('field:name', None)

        class ABSheetReferenceType(SheetReferenceType):
            source_isheet = IABSheet
            source_isheet_field = 'name'

        self.objectmap.connect(self.source, self.target, ASheetReferenceType)
        self.objectmap.connect(self.source, self.target, ABSheetReferenceType)

        result = self._make_one(self.target, IASheet)
        assert result == {'name': [self.source, self.source]}

    def test_with_isheet_that_has_subclass_with_extra_field(self):
        from adhocracy.interfaces import SheetReferenceType
        from adhocracy.interfaces import ISheet

        class IASheet(ISheet):
            taggedValue('field:name', None)

        class ASheetReferenceType(SheetReferenceType):
            source_isheet = IASheet
            source_isheet_field = 'name'

        class IABSheet(IASheet):
            taggedValue('field:othername', None)

        class ABSheetReferenceType(SheetReferenceType):
            source_isheet = IABSheet
            source_isheet_field = 'othername'

        self.objectmap.connect(self.source, self.target, SheetReferenceType)
        self.objectmap.connect(self.source, self.target, ASheetReferenceType)
        self.objectmap.connect(self.source, self.target, ABSheetReferenceType)

        result = self._make_one(self.target, IASheet)
        assert result == {'name': [self.source], 'othername': [self.source]}


class GetReferencesForIsheetUnitTest(unittest.TestCase):

    def _make_one(self, context, isheet):
        from adhocracy.graph import get_references_for_isheet
        return get_references_for_isheet(context, isheet)

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap = context.__objectmap__
        self.source = create_dummy_resource(parent=context)
        self.target = create_dummy_resource(parent=context)

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

    def _make_one(self, context):
        from adhocracy.graph import get_follows
        return get_follows(context)

    def setUp(self):
        self.context = create_dummy_resource()

    @patch('adhocracy.graph.get_references', autospec=True)
    def test_with_sucessor(self, dummy_references_template=None):
        precessor = create_dummy_resource()
        precessors = iter([(None, None, None, precessor)])
        dummy_references_template.return_value = precessors

        result = list(self._make_one(self.context))

        assert dummy_references_template.call_args[0][0] == self.context
        assert dummy_references_template.call_args[1]['base_reftype'] ==\
            NewVersionToOldVersion
        assert result == [precessor]

    @patch('adhocracy.graph.get_references', autospec=True)
    def test_without_sucessor(self, dummy_references_template=None):
        dummy_references_template.return_value = iter([])
        result = list(self._make_one(self.context))
        assert result == []


class GetFollowedByUnitTest(unittest.TestCase):

    def _make_one(self, context):
        from adhocracy.graph import get_followed_by
        return get_followed_by(context)

    def setUp(self):
        self.context = create_dummy_resource()

    @patch('adhocracy.graph.get_back_references', autospec=True)
    def test_with_sucessor(self, dummy_back_references=None):
        successor = create_dummy_resource()
        successors = iter([(successor, None, None, None)])
        dummy_back_references.return_value = successors

        result = list(self._make_one(self.context))

        assert dummy_back_references.call_args[0][0] == self.context
        assert dummy_back_references.call_args[1]['base_reftype'] ==\
            NewVersionToOldVersion
        assert result == [successor]

    @patch('adhocracy.graph.get_back_references', autospec=True)
    def test_without_sucessor(self, dummy_back_references=None):
        dummy_back_references.return_value = iter([])
        result = list(self._make_one(self.context))
        assert result == []


class IsInSubtreeUnitTest(unittest.TestCase):

    def _make_one(self, descendant, ancestors):
        from adhocracy.graph import is_in_subtree
        return is_in_subtree(descendant, ancestors)

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.context = context
        child = create_dummy_resource(parent=context)
        self.child = child

    def test_with_none_ancestor(self):
        """False if ancestors is None."""
        with pytest.raises(AssertionError):
            self._make_one(self.child, None)

    def test_with_no_ancestors(self):
        """False if ancestors is an empty list."""
        result = self._make_one(self.child, [])
        assert result is False

    def test_with_none_descendant(self):
        """False if descendant is None."""
        with pytest.raises(AssertionError):
            self._make_one(None, [self.child])

    def test_with_just_none(self):
        """False if ancestors and descendant are both None."""
        with pytest.raises(AssertionError):
            self._make_one(None, None)

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
