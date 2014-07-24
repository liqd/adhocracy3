import unittest

from pyramid import testing

from adhocracy.resources.pool import Pool
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import IItemVersionNewVersionAdded
from adhocracy.interfaces import IItemVersion

##########
# Helper #
##########


class DummyFolder(testing.DummyResource):

    def add(self, name, obj, **kwargs):
        self[name] = obj
        obj.__name__ = name
        obj.__parent__ = self
        obj.__oid__ = 1

    def check_name(self, name):
        return name

    def next_name(self, obj, prefix=''):
        return prefix + '_0000000' + str(obj.__oid__)


def _add_resource_type_to_registry(metadata, registry):
    from adhocracy.resources import ResourceFactory
    iresource = metadata.iresource
    registry.content.add(iresource.__identifier__,
                         iresource.__identifier__,
                         ResourceFactory(metadata))


################################
# Tests                        #
################################


class ItemVersionIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.graph import Graph
        from substanced.objectmap import ObjectMap
        self.config = testing.setUp()
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.sheets.name')
        self.config.include('adhocracy.sheets.versions')
        self.config.include('adhocracy.resources.itemversion')
        context = Pool()
        context.__objectmap__ = ObjectMap(context)
        context.__graph__ = Graph(context)
        self.context = context
        self.objectmap = context.__objectmap__
        self.graph = context.__graph__

    def tearDown(self):
        testing.tearDown()

    def _make_one(self, root_versions=[], follows=[], appstructs={}, creator=None):
        from adhocracy.sheets.versions import IVersionable
        parent = self.context
        follow = {IVersionable.__identifier__: {'follows': follows}}
        appstructs = appstructs or {}
        appstructs.update(follow)
        itemversion = self.config.registry.content.create(
            IItemVersion.__identifier__,
            parent=parent,
            appstructs=appstructs,
            creator=creator,
            root_versions=root_versions)
        return itemversion

    def test_registry_factory(self):
        content_types = self.config.registry.content.factory_types
        assert IItemVersion.__identifier__ in content_types

    def test_create(self):
        version_0 = self._make_one()
        assert IItemVersion.providedBy(version_0)

    def test_create_new_version(self):
        events = []
        listener = lambda event: events.append(event)
        self.config.add_subscriber(listener, IItemVersionNewVersionAdded)
        creator = self._make_one()

        version_0 = self._make_one()
        version_1 = self._make_one(follows=[version_0], creator=creator)

        assert len(events) == 1
        assert events[0].object == version_0
        assert events[0].new_version == version_1
        assert events[0].creator == creator

    def test_create_new_version_with_referencing_resources(self):
        events = []
        listener = lambda event: events.append(event)
        self.config.add_subscriber(listener, ISheetReferencedItemHasNewVersion)
        creator = self._make_one()

        version_0 = self._make_one()
        other_version_0 = self._make_one()
        self.objectmap.connect(other_version_0, version_0, SheetToSheet)
        self._make_one(follows=[version_0], creator=creator)

        assert len(events) == 1
        assert events[0].creator == creator

    def test_autoupdate_with_referencing_items(self):
        # for more tests see adhocracy.subscriber
        from adhocracy.sheets.document import ISection
        from adhocracy.resources.itemversion import itemversion_metadata
        self.config.include('adhocracy.sheets.document')
        self.config.include('adhocracy.subscriber')

        metadata = itemversion_metadata._replace(
            extended_sheets=[ISection])
        _add_resource_type_to_registry(metadata, self.config.registry)

        child_v0 = self._make_one()
        appstructs = {ISection.__identifier__: {'subsections': [child_v0]}}
        root_v0 = self._make_one(appstructs=appstructs)
        child_v1 = self._make_one(follows=[child_v0], root_versions=[root_v0])
        root_v0_followed_by = list(self.graph.get_followed_by(root_v0))
        assert len(root_v0_followed_by) == 2


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.itemversion')

    def tearDown(self):
        testing.tearDown()


