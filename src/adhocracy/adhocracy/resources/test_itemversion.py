import unittest

from pyramid import testing


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

################################
# Tests                        #
################################


class ItemVersionIntegrationTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        from adhocracy.folder import ResourcesAutolNamingFolder
        from adhocracy.resources.itemversion import itemversion_meta_defaults
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.resources')
        self.config.include('adhocracy.sheets.name')
        self.config.include('adhocracy.sheets.versions')
        context = ResourcesAutolNamingFolder()
        context.__objectmap__ = ObjectMap(context)
        self.context = context
        self.metadata = itemversion_meta_defaults

    def tearDown(self):
        testing.tearDown()

    def make_one(self, root_versions=[], follows=[], appstructs={}):
        from adhocracy.resources import ResourceFactory
        from adhocracy.sheets.versions import IVersionable
        if not appstructs:
            appstructs = {}
        if follows:
            appstructs.update({IVersionable.__identifier__:
                                   {'follows': follows}})
        return ResourceFactory(self.metadata)(parent=self.context,
                                              appstructs=appstructs,
                                              root_versions=root_versions)

    def test_create_without_referencing_items(self):
        from adhocracy.interfaces import IItemVersion
        from adhocracy.interfaces import IItemVersionNewVersionAdded
        events = []

        def listener(event):
            events.append(event)
        self.config.add_subscriber(listener, IItemVersionNewVersionAdded)

        old_version = self.make_one()
        new_version = self.make_one(follows=[old_version],
                                    root_versions=[old_version])

        assert IItemVersion.providedBy(new_version)
        assert len(events) == 1
        assert IItemVersionNewVersionAdded.providedBy(events[0])

    def test_create_with_referencing_items(self):
        from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
        from adhocracy.interfaces import SheetToSheet
        events = []

        def listener(event):
            events.append(event)
        self.config.add_subscriber(listener, ISheetReferencedItemHasNewVersion)

        other_version = self.make_one()
        old_version = self.make_one()
        om = self.context.__objectmap__
        om.connect(other_version, old_version, SheetToSheet)
        self.make_one(follows=[old_version],
                      root_versions=[old_version])

        assert len(events) == 2

    def test_autoupdate_with_referencing_items(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.interfaces import IItemVersion
        from adhocracy.sheets.document import ISection
        from adhocracy.sheets.versions import IVersionableFollowsReference
        # for more tests see adhocracy.subscriber
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.sheets.document')
        self.config.include('adhocracy.subscriber')

        class ISectionVersion(IItemVersion):
            pass
        self.metadata = self.metadata._replace(iresource=ISectionVersion,
                                               extended_sheets=[ISection])
        self.config.registry.content.add(ISectionVersion.__identifier__,
                                         ISectionVersion.__identifier__,
                                         ResourceFactory(self.metadata))
        child = self.make_one()
        root = self.make_one(appstructs={ISection.__identifier__:
                                         {'subsections': [child]}})
        self.make_one(follows=[child], root_versions=[root])
        om = self.context.__objectmap__
        root_followed_by = list(om.sources(root, IVersionableFollowsReference))
        assert len(root_followed_by) == 1


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.itemversion')
        self.context = DummyFolder()

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        from adhocracy.interfaces import IItemVersion
        content_types = self.config.registry.content.factory_types
        assert IItemVersion.__identifier__ in content_types

    def test_includeme_registry_create_content(self):
        from adhocracy.interfaces import IItemVersion
        res = self.config.registry.content.create(IItemVersion.__identifier__,
                                                  self.context)
        assert IItemVersion.providedBy(res)
