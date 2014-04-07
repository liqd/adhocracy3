from adhocracy.folder import ResourcesAutolNamingFolder
from adhocracy.interfaces import AdhocracyReferenceType
from adhocracy.interfaces import IItemVersion
from adhocracy.resources import ResourceFactory
from adhocracy.sheets.versions import IVersionableFollowsReference
from pyramid import testing
from substanced.objectmap import ObjectMap
from . import is_in_subtree

import unittest


class GraphUnitTest(unittest.TestCase):

    def new_objectid(self):
        return self.objectmap.new_objectid()

    def make_one(self, iface=None, appstructs={}):
        """Make a resource ."""
        return ResourceFactory(iface or IItemVersion)(self.context,
                                                      appstructs=appstructs)
    def setUp(self):
        self.config = testing.setUp()
        context = ResourcesAutolNamingFolder()
        context.__objectmap__ = ObjectMap(context)
        self.context = context
        self.child = self.make_one()

    def tearDown(self):
        testing.tearDown()

    def test_is_in_subtree_with_none_ancestor(self):
        """False if ancestors is None."""
        result = is_in_subtree(self.child, None)
        assert result is False

    def test_is_in_subtree_with_no_ancestors(self):
        """False if ancestors is an empty list."""
        result = is_in_subtree(self.child, [])
        assert result is False


    def test_is_in_subtree_with_none_descendant(self):
        """False if descendant is None."""
        result = is_in_subtree(None, [self.child])
        assert result is False

    def test_is_in_subtree_with_just_none(self):
        """False if ancestors and descendant are both None."""
        result = is_in_subtree(None, None)
        assert result is False

    def test_is_in_subtree_of_itself(self):
        """True if both are the same resource."""
        result = is_in_subtree(self.child, [self.child])
        assert result is True

    def test_is_in_subtree_direct_link(self):
        """True if direct AdhocracyReferenceType link from ancestor to
        descendent.

        """
        root = self.make_one()
        element = self.make_one()
        om = self.context.__objectmap__
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
        other_version = self.make_one()
        old_version = self.make_one()
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
        grandma = self.make_one()
        dad = self.make_one()
        daugher = self.make_one()
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
        dad = self.make_one()
        daugher = self.make_one()
        step_son = self.make_one()
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
        root = self.make_one()
        not_root = self.make_one()
        element = self.make_one()
        om = self.context.__objectmap__
        om.connect(root, element, AdhocracyReferenceType)
        result = is_in_subtree(element, [root, not_root])
        assert result is True
        result = is_in_subtree(element, [not_root, root])
        assert result is True
