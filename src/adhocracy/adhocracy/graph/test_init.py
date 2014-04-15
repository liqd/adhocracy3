from adhocracy.interfaces import IResource
from adhocracy.interfaces import AdhocracyReferenceType
from pyramid import testing

from . import collect_reftypes
from . import is_in_subtree

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


class GraphUnitTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        context = create_dummy_resource()
        context.__objectmap__ = ObjectMap(context)
        self.context = context
        child = create_dummy_resource(parent=context)
        self.child = child

    def test_is_in_subtree_with_none_ancestor(self):
        """False if ancestors is None."""
        with pytest.raises(AssertionError):
            is_in_subtree(self.child, None)

    def test_is_in_subtree_with_no_ancestors(self):
        """False if ancestors is an empty list."""
        result = is_in_subtree(self.child, [])
        assert result is False

    def test_is_in_subtree_with_none_descendant(self):
        """False if descendant is None."""
        with pytest.raises(AssertionError):
            is_in_subtree(None, [self.child])

    def test_is_in_subtree_with_just_none(self):
        """False if ancestors and descendant are both None."""
        with pytest.raises(AssertionError):
            is_in_subtree(None, None)

    def test_is_in_subtree_of_itself(self):
        """True if both are the same resource."""
        result = is_in_subtree(self.child, [self.child])
        assert result is True

    def test_is_in_subtree_direct_link(self):
        """True if direct AdhocracyReferenceType link from ancestor to
        descendent.

        """
        root = create_dummy_resource(parent=self.context)
        element = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.object_for(root.__oid__)
        om.connect(root, element, AdhocracyReferenceType)
        result = is_in_subtree(element, [root])
        assert result is True
        # Inverse relation should NOT be found
        result = is_in_subtree(root, [element])
        assert result is False

    def test_is_in_subtree_direct_follows_link(self):
        """False if direct IVersionableFollowsReference link from ancestor to
        descendent.

        """
        from adhocracy.sheets.versions import IVersionableFollowsReference
        other_version = create_dummy_resource(parent=self.context)
        old_version = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(other_version, old_version, IVersionableFollowsReference)
        result = is_in_subtree(old_version, [other_version])
        assert result is False
        # Inverse relation should not be found either
        result = is_in_subtree(other_version, [old_version])
        assert result is False

    def test_is_in_subtree_indirect_link(self):
        """True if two-level AdhocracyReferenceType link from ancestor to
        descendent.

        """
        grandma = create_dummy_resource(parent=self.context)
        dad = create_dummy_resource(parent=self.context)
        daugher = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(grandma, dad, AdhocracyReferenceType)
        om.connect(dad, daugher, AdhocracyReferenceType)
        result = is_in_subtree(daugher, [grandma])
        assert result is True
        # Inverse relation should NOT be found
        result = is_in_subtree(grandma, [daugher])
        assert result is False

    def test_is_in_subtree_indirect_follows_link(self):
        """True if two-level link from ancestor to descendent that includes a
        follows relation.

        """
        from adhocracy.sheets.versions import IVersionableFollowsReference
        dad = create_dummy_resource(parent=self.context)
        daugher = create_dummy_resource(parent=self.context)
        step_son = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(dad, daugher, AdhocracyReferenceType)
        om.connect(step_son, daugher, IVersionableFollowsReference)
        result = is_in_subtree(step_son, [dad])
        assert result is False
        # Inverse relation should not be found either
        result = is_in_subtree(dad, [step_son])
        assert result is False

    def test_ancestor_list_has_multiple_elements(self):
        """True if ancestors is a two-element list and one of them is the right
        one.

        """
        root = create_dummy_resource(parent=self.context)
        not_root = create_dummy_resource(parent=self.context)
        element = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(root, element, AdhocracyReferenceType)
        result = is_in_subtree(element, [root, not_root])
        assert result is True
        result = is_in_subtree(element, [not_root, root])
        assert result is True

    def test_collect_reftypes_with_empty_objectmap_and_default_excludes(self):
        """No relations in objectmap, so result should be empty."""
        om = self.context.__objectmap__
        result = collect_reftypes(om)
        assert result == []

    def test_collect_reftypes_with_empty_objectmap_and_None_excludes(self):
        """No relations in objectmap, so result should be empty."""
        om = self.context.__objectmap__
        result = collect_reftypes(om, None)
        assert result == []

    def test_collect_reftypes_two_types(self):
        """Two reftypes in objectmap, both should be found."""
        dad = create_dummy_resource(parent=self.context)
        daugher = create_dummy_resource(parent=self.context)
        step_son = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(dad, daugher, AdhocracyReferenceType)

        class IOtherReferenceType(AdhocracyReferenceType):
            pass
        om.connect(step_son, daugher, IOtherReferenceType)
        result = collect_reftypes(om)
        assert len(result) == 2
        assert AdhocracyReferenceType in result
        assert IOtherReferenceType in result

    def test_collect_reftypes_one_excluded(self):
        """Two reftypes in OM, one is excluded, the other should be found."""
        dad = create_dummy_resource(parent=self.context)
        daugher = create_dummy_resource(parent=self.context)
        step_son = create_dummy_resource(parent=self.context)
        om = self.context.__objectmap__
        om.connect(dad, daugher, AdhocracyReferenceType)

        class IOtherReferenceType(AdhocracyReferenceType):
            pass
        om.connect(step_son, daugher, IOtherReferenceType)
        result = collect_reftypes(om, [AdhocracyReferenceType])
        assert len(result) == 1
        assert IOtherReferenceType in result
        assert AdhocracyReferenceType not in result
