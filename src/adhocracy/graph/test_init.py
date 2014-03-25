from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IResource
from adhocracy.sheets.document import IDocument
from adhocracy.sheets.versions import IVersionable
from pyramid import testing
from substanced.objectmap import ObjectMap
from . import is_ancestor

import unittest


class DummyFolder(testing.DummyResource):

    def add(self, name, obj, **kwargs):
        self[name] = obj
        obj.__name__ = name
        obj.__parent__ = self
        obj.__oid__ = 1

    def check_name(self, name):
        if name == 'invalid':
            raise ValueError
        return name

    def next_name(self, obj, prefix=''):
        return prefix + '_0000000'


class GraphUnitTest(unittest.TestCase):

    def make_one(self, oid, provides=(IResource, IVersionable),
            appstruct={}):
        """Make a resource."""
        resource = testing.DummyResource(__parent__=self.parent,
                                         __oid__=oid,
                                         __provides__=provides
                                         )
        resource.dummy_appstruct = appstruct
        return resource

    def setUp(self):
        self.config = testing.setUp()
        context = DummyFolder()
        context.__objectmap__ = ObjectMap(context)
        self.context = context
        # create dummy parent (Item for versionables)
        self.parent = testing.DummyResource()
        # create dummy child with sheet data (ItemVersion for versionables)
        self.child = self.make_one(0,
                appstruct={IVersionable.__identifier__: {'follows': [-1]}}
        )

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
        """True if direct 'elements' link from ancestor to descendent."""
        ancestor = self.make_one(1,
                appstruct={IDocument.__identifier__: {'elements': [self.child.__oid__]}}
        )
        # TODO fix errors -- resources not connected to objectmap
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
