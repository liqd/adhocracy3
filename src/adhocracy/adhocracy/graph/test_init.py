from adhocracy.interfaces import IResource
from adhocracy.interfaces import SheetToSheet
from mock import patch
from pyramid import testing
from zope.interface import taggedValue

import unittest
import pytest

############
#  helper  #
############


def create_dummy_resource(parent=None, iface=IResource):
    """Create dummy resrouce and add it to the parent objectmap."""
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

    def _make_one(self, objectmap, base_reftype=None):
        from . import _get_reftypes
        return _get_reftypes(objectmap, base_reftype=base_reftype)

    @patch('substanced.objectmap.ObjectMap', autospec=True)
    def setUp(self, dummy_objectmap=None):
        self.objectmap = dummy_objectmap.return_value

    def test_empty_objectmap_and_default_excludes(self):
        """No relations in objectmap, so result should be empty."""
        om = self.objectmap
        om.get_reftypes.return_value = []
        result = self._make_one(om)
        assert result == []

    def test_empty_objectmap_and_no_base_type(self):
        """No relations in objectmap, so result should be empty."""
        om = self.objectmap
        om.get_reftypes.return_value = []
        result = self._make_one(om, [])
        assert result == []

    def test_one_wrong_refernce_type(self):
        """Wrong ReferenceType in objectmap, so result should be empty. """
        om = self.objectmap
        om.get_reftypes.return_value = ["NoneSheetToSheet"]
        result = self._make_one(om, [])
        assert result == []

    def test_two_reference_types(self):
        """Two reftypes in objectmap, both should be found."""

        class IOtherReferenceType(SheetToSheet):
            pass
        om = self.objectmap
        om.get_reftypes.return_value = [IOtherReferenceType,
                                        SheetToSheet]
        result = self._make_one(om)
        assert len(result) == 2
        assert SheetToSheet in result
        assert IOtherReferenceType in result

    def test_two_reference_types_with_base_reftype(self):
        """Two reftypes in OM, one is excluded, the other should be found."""

        class IOtherReferenceType(SheetToSheet):
            pass
        om = self.objectmap
        om.get_reftypes.return_value = [IOtherReferenceType,
                                        SheetToSheet]
        result = self._make_one(om, base_reftype=IOtherReferenceType)
        assert len(result) == 1
        assert IOtherReferenceType in result
        assert SheetToSheet not in result


class ReferencesTemplateUnitTest(unittest.TestCase):

    def _make_one(self, objectmap_method, context, **kwargs):
        from . import _references_template
        return _references_template(objectmap_method, context, **kwargs)

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap_method = ObjectMap.sources
        self.objectmap = context.__objectmap__
        self.resource = create_dummy_resource(parent=context)

    def test_no_reference(self):
        result = self._make_one(self.objectmap_method, self.resource)
        assert list(result) == []

    def test_no_sheetreferences(self):
        from substanced.interfaces import ReferenceType
        self.objectmap.connect(self.resource, self.resource, ReferenceType)
        result = self._make_one(self.objectmap_method, self.resource)
        assert list(result) == []

    def test_sheetreferences(self):
        from adhocracy.interfaces import SheetReferenceType
        self.objectmap.connect(self.resource, self.resource,
                               SheetReferenceType)

        result = self._make_one(self.objectmap_method, self.resource)

        resource, isheet, isheet_field = result.__next__()
        assert resource == self.resource
        assert isheet == SheetReferenceType.getTaggedValue('source_isheet')
        assert isheet_field == \
            SheetReferenceType.getTaggedValue('source_isheet_field')

    def test_with_base_reftype(self):
        from adhocracy.interfaces import SheetReferenceType

        class ASheetReferenceType(SheetReferenceType):
            pass

        class ABSheetReferenceType(ASheetReferenceType):
            pass
        self.objectmap.connect(self.resource, self.resource,
                               SheetReferenceType)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)
        self.objectmap.connect(self.resource, self.resource,
                               ABSheetReferenceType)

        result = self._make_one(self.objectmap_method, self.resource,
                                base_reftype=ASheetReferenceType)
        assert len(list(result)) == 2

    def test_with_source_isheet(self):
        from adhocracy.interfaces import SheetReferenceType
        from adhocracy.interfaces import ISheet

        class IASheet(ISheet):
            pass

        class ASheetReferenceType(SheetReferenceType):
            source_isheet = IASheet

        self.objectmap.connect(self.resource, self.resource,
                               SheetReferenceType)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)

        result = self._make_one(self.objectmap_method, self.resource,
                                source_isheet=IASheet)
        assert len(list(result)) == 1

    def test_with_source_isheet_that_has_subclass(self):
        from adhocracy.interfaces import SheetReferenceType
        from adhocracy.interfaces import ISheet

        class IASheet(ISheet):
            pass

        class ASheetReferenceType(SheetReferenceType):
            source_isheet = IASheet

        self.objectmap.connect(self.resource, self.resource,
                               SheetReferenceType)
        self.objectmap.connect(self.resource, self.resource,
                               ASheetReferenceType)

        result = self._make_one(self.objectmap_method, self.resource,
                                source_isheet=ISheet)
        assert len(list(result)) == 2


class GetReferencesUnitTest(unittest.TestCase):

    def _make_one(self, context):
        from . import get_references
        return get_references(context)

    def setUp(self):
        self.context = create_dummy_resource()

    @patch('adhocracy.graph._references_template', autospec=True)
    def test_with_resource(self, dummy_references_template=None):
        from substanced.objectmap import ObjectMap
        self._make_one(self.context)
        assert dummy_references_template.call_args[0][0] == ObjectMap.targets
        assert dummy_references_template.call_args[0][1] == self.context


class GetBackReferencesUnitTest(unittest.TestCase):

    def _make_one(self, context):
        from . import get_back_references
        return get_back_references(context)

    def setUp(self):
        self.context = create_dummy_resource()

    @patch('adhocracy.graph._references_template', autospec=True)
    def test_with_resource(self, dummy_references_template=None):
        from substanced.objectmap import ObjectMap
        self._make_one(self.context)
        assert dummy_references_template.call_args[0][0] == ObjectMap.sources
        assert dummy_references_template.call_args[0][1] == self.context


class GetBackReferencesForIsheetUnitTest(unittest.TestCase):

    def _make_one(self, context, isheet):
        from . import get_back_references_for_isheet
        return get_back_references_for_isheet(context, isheet)

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap = context.__objectmap__
        self.source = create_dummy_resource(parent=context)
        self.target = create_dummy_resource(parent=context)

    def test_with_isheet(self):
        from adhocracy.interfaces import SheetReferenceType
        from adhocracy.interfaces import ISheet

        class IASheet(ISheet):
            taggedValue('field:name', None)

        class ASheetReferenceType(SheetReferenceType):
            source_isheet = IASheet
            source_isheet_field = 'name'
        self.objectmap.connect(self.source, self.target, ASheetReferenceType)

        result = self._make_one(self.target, IASheet)

        wanted = {ASheetReferenceType.getTaggedValue('source_isheet_field'):
                  [self.source]}
        assert result == wanted

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
        wanted = {ASheetReferenceType.getTaggedValue('source_isheet_field'):
                  [self.source, self.source]}
        assert result == wanted

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
        wanted = {ASheetReferenceType.getTaggedValue('source_isheet_field'):
                  [self.source]}
        assert result == wanted


class GetReferencesForIsheetUnitTest(unittest.TestCase):

    def _make_one(self, context, isheet):
        from . import get_references_for_isheet
        return get_references_for_isheet(context, isheet)

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.objectmap = context.__objectmap__
        self.source = create_dummy_resource(parent=context)
        self.target = create_dummy_resource(parent=context)

    def test_with_isheet(self):
        from adhocracy.interfaces import SheetReferenceType
        from adhocracy.interfaces import ISheet

        class IASheet(ISheet):
            taggedValue('field:name', None)

        class ASheetReferenceType(SheetReferenceType):
            source_isheet = IASheet
            source_isheet_field = 'name'
        self.objectmap.connect(self.source, self.target, ASheetReferenceType)

        result = self._make_one(self.source, IASheet)

        wanted = {ASheetReferenceType.getTaggedValue('source_isheet_field'):
                  [self.target]}
        assert result == wanted


class IsInSubtreeUnitTest(unittest.TestCase):

    def _make_one(self, descendant, ancestors):
        from . import is_in_subtree
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
        """False if direct IVersionableFollowsReference link from ancestor to
        descendent.

        """
        from adhocracy.sheets.versions import IVersionableFollowsReference
        other_version = create_dummy_resource(parent=self.context)
        old_version = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(other_version, old_version, IVersionableFollowsReference)
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
        from adhocracy.sheets.versions import IVersionableFollowsReference
        dad = create_dummy_resource(parent=self.context)
        daugher = create_dummy_resource(parent=self.context)
        step_son = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(dad, daugher, SheetToSheet)
        om.connect(step_son, daugher, IVersionableFollowsReference)
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



