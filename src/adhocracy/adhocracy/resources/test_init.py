from adhocracy.interfaces import ISheet
from pyramid import testing

import pytest
import unittest


#############
#  helpers  #
#############

class ISheetY(ISheet):
    pass


class ISheetX(ISheet):
    pass


class DummyPropertySheetAdapter(object):

    readonly = False

    def __init__(self, context, iface):
        self.context = context
        self.iface = iface
        if 'dummy_appstruct' not in self.context:
            self.context['dummy_appstruct'] = {}
        if 'dummy_cstruct' not in self.context:
            self.context['dummy_cstruct'] = {}

    def set(self, appstruct):
        self.context['dummy_appstruct'].update(appstruct)

    def get(self):
        return self.context['dummy_appstruct']

    def set_cstruct(self, cstruct):
        self.context['dummy_cstruct'].update(cstruct)


def _register_dummypropertysheet_adapter(config):
    from adhocracy.interfaces import IResourcePropertySheet
    from adhocracy.interfaces import ISheet
    from zope.interface.interfaces import IInterface
    config.registry.registerAdapter(DummyPropertySheetAdapter,
                                    (ISheet, IInterface),
                                    IResourcePropertySheet)


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


###########
#  tests  #
###########

class ItemIntegrationTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.resources')
        self.config.include('adhocracy.sheets.name')
        self.config.include('adhocracy.sheets.tags')
        context = DummyFolder()
        context.__objectmap__ = ObjectMap(context)
        self.context = context

    def tearDown(self):
        testing.tearDown()

    def make_one(self):
        from adhocracy.interfaces import IItem
        from . import ResourceFactory
        return ResourceFactory(IItem)(self.context)

    def test_create(self):
        from adhocracy.interfaces import IItemVersion
        from adhocracy.interfaces import ITag

        inst = self.make_one()

        item_version = inst['VERSION_0000000']
        item_version_oid = item_version.__oid__
        first = inst['FIRST']
        last = inst['LAST']
        assert IItemVersion.providedBy(item_version)
        assert ITag.providedBy(first)
        assert ITag.providedBy(last)
        wanted = {'adhocracy.sheets.tags.ITag': {'elements':
                                                 [item_version_oid]},
                  'adhocracy.sheets.name.IName': {'name': 'FIRST'}}
        assert first._propertysheets == wanted
        wanted = {'adhocracy.sheets.tags.ITag': {'elements':
                                                 [item_version_oid]},
                  'adhocracy.sheets.name.IName': {'name': 'LAST'}}
        assert last._propertysheets == wanted


class ItemVersionIntegrationTest(unittest.TestCase):

    def setUp(self):
        from substanced.objectmap import ObjectMap
        # TODO make unittest instead of intergration test.
        from adhocracy.folder import ResourcesAutolNamingFolder
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.resources')
        self.config.include('adhocracy.sheets.name')
        self.config.include('adhocracy.sheets.versions')
        context = ResourcesAutolNamingFolder()
        context.__objectmap__ = ObjectMap(context)
        self.context = context

    def tearDown(self):
        testing.tearDown()

    def make_new_version_data(self, follows_oid):
        """Create a versionable sheet with follows field.

        Args:
            follows_oid (int): OID of preceding version (follows)

        """

        from adhocracy.sheets.versions import IVersionable
        return {
            IVersionable.__identifier__: {
                'follows': [follows_oid],
                }
            }

    def make_one(self, iface=None, appstructs={}, root_versions=[]):
        from adhocracy.interfaces import IItemVersion
        from . import ResourceFactory
        return ResourceFactory(iface or IItemVersion)(self.context,
                                                      appstructs=appstructs,
                                                      options=root_versions)

    def test_create_without_referencing_items(self):
        from adhocracy.interfaces import IItemVersion
        from adhocracy.interfaces import IItemNewVersionAdded
        events = []

        def listener(event):
            events.append(event)
        self.config.add_subscriber(listener, IItemNewVersionAdded)

        old_version = self.make_one()
        new_version_data = self.make_new_version_data(old_version.__oid__)
        new_version = self.make_one(appstructs=new_version_data,
                      root_versions=[old_version])

        assert IItemVersion.providedBy(new_version)
        assert len(events) == 1
        assert IItemNewVersionAdded.providedBy(events[0])

    def test_create_with_referencing_items(self):
        from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
        from adhocracy.interfaces import AdhocracyReferenceType
        from adhocracy.interfaces import ISheet
        from adhocracy.sheets.versions import IVersionable
        events = []

        def listener(event):
            events.append(event)
        self.config.add_subscriber(listener, ISheetReferencedItemHasNewVersion)

        other_version = self.make_one()
        old_version = self.make_one()
        om = self.context.__objectmap__
        om.connect(other_version, old_version, AdhocracyReferenceType)
        new_version_data = self.make_new_version_data(old_version.__oid__)
        self.make_one(appstructs=new_version_data,
                      root_versions=[old_version])

        assert len(events) == 2
        assert ISheetReferencedItemHasNewVersion.providedBy(events[0])
        assert events[0].isheet == ISheet
        assert events[1].isheet == IVersionable

    def test_autoupdate_with_referencing_items(self):
        from adhocracy.interfaces import IItemVersion
        from adhocracy.sheets.document import ISection
        from adhocracy.sheets.versions import IVersionableFollowsReference
        from zope.interface import taggedValue
        # add autoupdate sheet for more tests see adhocracy.subscriber
        self.config.include('adhocracy.sheets.document')
        self.config.include('adhocracy.subscriber')

        class ISectionVersion(IItemVersion):
            taggedValue('extended_sheets', set([ISection]))

        child = self.make_one(iface=ISectionVersion)
        root = self.make_one(iface=ISectionVersion,
                             appstructs={ISection.__identifier__:
                                         {"subsections": [child.__oid__]}})
        new_version_data = self.make_new_version_data(child.__oid__)
        self.make_one(iface=ISectionVersion,
                      appstructs=new_version_data,
                      root_versions=[root])
        om = self.context.__objectmap__
        root_followed_by = list(om.sources(root, IVersionableFollowsReference))
        assert len(root_followed_by) == 1


class ResourceFactoryUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        context = DummyFolder()
        self.context = context

    def tearDown(self):
        testing.tearDown()

    def make_one(self, iface):
        from . import ResourceFactory
        return ResourceFactory(iface)

    def test_create(self):
        from adhocracy.interfaces import IResource
        inst = self.make_one(IResource)
        assert '__call__' in dir(inst)

    def test_valid_IResource(self):
        from zope.interface.verify import verifyObject
        from adhocracy.interfaces import IResource
        from persistent.interfaces import IPersistent
        from zope.interface import directlyProvidedBy
        inst = self.make_one(IResource)
        resource = inst(self.context)

        assert IPersistent.providedBy(resource)
        assert IResource in directlyProvidedBy(resource)
        assert verifyObject(IResource, resource)

    def test_valid_IItemVersion(self):
        from adhocracy.interfaces import IItemVersion
        inst = self.make_one(IItemVersion)
        resource = inst(self.context)
        assert IItemVersion.providedBy(resource)

    def test_valid_add_to_context(self):
        from adhocracy.interfaces import IResource
        inst = self.make_one(IResource)
        resource = inst(self.context)
        assert resource.__parent__ == self.context
        assert resource.__name__ in self.context
        assert resource.__oid__ == 1

    def test_valid_non_add_to_context(self):
        from adhocracy.interfaces import IResource
        inst = self.make_one(IResource)
        resource = inst(self.context, add_to_context=False)
        assert resource.__parent__ is None
        assert resource.__name__ == ''
        assert not hasattr(resource, '__oid__')

    def test_valid_dotted_resource_iface(self):
        from adhocracy.interfaces import IResource
        from zope.interface import directlyProvidedBy
        inst = self.make_one(IResource.__identifier__)
        resource = inst(self.context)
        assert IResource in directlyProvidedBy(resource)

    def test_valid_non_dotted_sheet_ifaces(self):
        from zope.interface import taggedValue
        from adhocracy.interfaces import IResource

        class IResourceType(IResource):
            taggedValue('extended_sheets', set([ISheetX]))
            taggedValue('basic_sheets', set([ISheetY]))

        inst = self.make_one(IResourceType)
        resource = inst(self.context)

        assert ISheetX.providedBy(resource)
        assert ISheetY.providedBy(resource)

    def test_valid_after_create(self):
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        def dummy_after_create(context, registry, options):
            context._options = options
            context._registry = registry

        class IResourceType(IResource):
            taggedValue('after_creation', [dummy_after_create])

        inst = self.make_one(IResourceType)
        resource = inst(self.context, kwarg1=True)

        assert resource._options == {"kwarg1": True}
        assert resource._registry is self.config.registry

    def test_valid_no_run_after_create(self):
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        def dummy_after_create(context, registry, options):
            context.test = 'aftercreate'

        class IResourceType(IResource):
            taggedValue('after_creation', [dummy_after_create])

        inst = self.make_one(IResourceType)
        resource = inst(self.context, run_after_creation=False)
        with pytest.raises(AttributeError):
            resource.test

    def test_valid_with_appstructs_data(self):
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        class IResourceType(IResource):
            taggedValue('basic_sheets', set([ISheetY]))

        data = {ISheetY.__identifier__: {"count": 0}}
        _register_dummypropertysheet_adapter(self.config)

        inst = self.make_one(IResourceType)
        resource = inst(self.context, appstructs=data)

        assert resource['dummy_appstruct'] == {'count': 0}

    def test_valid_with_appstructs_name_data(self):
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        class IResourceType(IResource):
            taggedValue('basic_sheets', set([ISheetY]))

        data = {"adhocracy.sheets.name.IName": {"name": "child"}}
        _register_dummypropertysheet_adapter(self.config)

        inst = self.make_one(IResourceType)
        resource = inst(self.context, appstructs=data)

        assert resource['dummy_appstruct'] == {'name': 'child'}

    def test_non_valid_with_appstructs_empty_name_data(self):
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        class IResourceType(IResource):
            taggedValue('basic_sheets', set([ISheetY]))

        data = {"adhocracy.sheets.name.IName": {"name": "invalid"}}
        _register_dummypropertysheet_adapter(self.config)

        inst = self.make_one(IResourceType)
        with pytest.raises(ValueError):
            inst(self.context, appstructs=data)


    def test_non_valid_missing_context(self):
        from adhocracy.interfaces import IResource
        with pytest.raises(TypeError):
            self.make_one(IResource)()

    def test_non_valid_wrong_iresource_iface(self):
        from zope.interface import Interface

        with pytest.raises(AssertionError):
            self.make_one(Interface)

    def test_non_valid_wrong_iproperty_iface(self):
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue
        from zope.interface import Interface

        class IResourceType(IResource):
            taggedValue('basic_sheets', set([Interface]))

        with pytest.raises(AssertionError):
            self.make_one(IResourceType)
