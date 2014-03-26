from adhocracy.interfaces import AdhocracyReferenceType
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IResource
from adhocracy.sheets.document import IDocument
from adhocracy.sheets.versions import IVersionable
from pyramid import testing
from substanced.objectmap import ObjectMap
from . import is_ancestor

import unittest


class GraphUnitTest(unittest.TestCase):

    def new_objectid(self):
        return self.objectmap.new_objectid()

    def make_one(self, path):
        """Make a resource ."""
        resource = testing.DummyResource(__parent__=self.context)
        self.objectmap.add(resource, (path,))
        return resource

    def setUp(self):
        self.config = testing.setUp()
        context = testing.DummyResource()
        self.objectmap =ObjectMap(context)
        context.__objectmap__ = self.objectmap
        self.objectmap.add(context, ('parent',))
        self.context = context
        # create dummy child
        self.child = self.make_one('child')

    def tearDown(self):
        testing.tearDown()

    def test_is_ancestor_with_none_ancestor(self):
        """False if ancestor is None."""
        result = is_ancestor(None, self.child)
        assert result is False

    def test_is_ancestor_with_none_descendant(self):
        """False if descendant is None."""
        result = is_ancestor(self.child, None)
        assert result is False

    def test_is_ancestor_with_just_none(self):
        """False if ancestor and descendant are both None."""
        result = is_ancestor(None, None)
        assert result is False

    def test_is_ancestor_of_itself(self):
        """True if both are the same resource."""
        result = is_ancestor(self.child, self.child)
        assert result is True

    def test_is_ancestor_direct_link(self):
        """True if direct AdhocracyReferenceType link from ancestor to descendent."""
        ancestor = self.make_one('anc')
        self.objectmap.connect(ancestor, self.child, AdhocracyReferenceType)
        assert [self.child] == list(self.objectmap.targets(ancestor,
            AdhocracyReferenceType))
        assert [ancestor] == list(self.objectmap.sources(self.child,
            AdhocracyReferenceType))
        result = is_ancestor(ancestor, self.child)
        assert result is True

## TODO
##    def test_is_ancestor_direct_link(self):
##        """"False if direct follows link from root to offspring."""
##        old_version = self.make_one()
##        new_version_data = {IVersionable.__identifier__:
##                            {'follows': [old_version.__oid__]}}
##        self.make_one(appstructs=new_version_data)
##        new_version = self.make_one()
##        result = is_ancestor(old_version, new_version)
##        assert result is False

# TODO True if indirect element/contains/comments link from A to D
# TODO False if C is element of A and D follows C
# TODO False if direct element link from D to A
