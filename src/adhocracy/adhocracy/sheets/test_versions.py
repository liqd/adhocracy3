import unittest

from pyramid import testing



############
#  helper  #
############

def create_dummy_resource(parent=None, iface=None):
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


class VersionsPropertySheetUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()

    def make_one(self, context):
        from adhocracy.sheets.versions import IVersions
        from .versions import PoolPropertySheetAdapter
        return PoolPropertySheetAdapter(context, IVersions)

    def test_create_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from adhocracy.sheets.pool import PoolPropertySheetAdapter
        from zope.interface.verify import verifyObject
        inst = self.make_one(self.context)
        assert verifyObject(IResourcePropertySheet, inst) is True
        assert isinstance(inst, PoolPropertySheetAdapter)

    def test_get_empty(self):
        inst = self.make_one(self.context)
        assert inst.get() == {'elements': []}

    def test_get_not_empty(self):
        from adhocracy.sheets.versions import IVersionable
        versionable = testing.DummyResource(__provides__=IVersionable,
                                            __oid__=1)
        self.context['child'] = versionable
        inst = self.make_one(self.context)
        assert inst.get() == {'elements': [versionable]}

    def test_get_not_empty_not_iversionable(self):
        non_versionable = testing.DummyResource()
        self.context['child'] = non_versionable
        inst = self.make_one(self.context)
        assert inst.get() == {'elements': []}


class VersionablePropertySheetUnitTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        from adhocracy.sheets.versions import IVersionable
        context = testing.DummyResource(__provides__=IVersionable,
                                        __oid__=0)
        self.objectmap = ObjectMap(context)
        context.__objectmap__ = self.objectmap
        self.context = context

    def make_one(self, context):
        from adhocracy.sheets.versions import IVersionable
        from .versions import VersionableSheetAdapter
        return VersionableSheetAdapter(context, IVersionable)

    def test_create_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from .versions import VersionableSheetAdapter
        from zope.interface.verify import verifyObject
        inst = self.make_one(self.context)
        assert verifyObject(IResourcePropertySheet, inst) is True
        assert isinstance(inst, VersionableSheetAdapter)

    def test_get_empty(self):
        inst = self.make_one(self.context)
        assert inst.get() == {'follows': [],
                              'followed_by': []}

    def test_get_with_followed_by(self):
        from .versions import IVersionable
        from .versions import IVersionableFollowsReference
        old = create_dummy_resource(self.context, IVersionable)
        new = create_dummy_resource(self.context, IVersionable)
        self.objectmap.connect(new, old, IVersionableFollowsReference)
        inst = self.make_one(old)
        assert inst.get() == {'follows': [],
                              'followed_by': [new]}


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def get_one(self, config, context, iface):
        from adhocracy.utils import get_sheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        return get_sheet(context, iface)

    def test_register_versions_adapter(self):
        from adhocracy.sheets.versions import IVersions
        from adhocracy.sheets.versions import PoolPropertySheetAdapter
        self.config.include('adhocracy.sheets.versions')
        inst = self.get_one(self.config, testing.DummyResource(), IVersions)
        assert isinstance(inst, PoolPropertySheetAdapter)
        assert inst.iface is IVersions

    def test_register_versionable_adapter(self):
        from adhocracy.sheets.versions import IVersionable
        from adhocracy.sheets.versions import VersionableSheetAdapter
        self.config.include('adhocracy.sheets.versions')
        inst = self.get_one(self.config, testing.DummyResource(), IVersionable)
        assert isinstance(inst, VersionableSheetAdapter)
        assert inst.iface is IVersionable
