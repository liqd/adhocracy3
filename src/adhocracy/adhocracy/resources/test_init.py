from adhocracy.sheets import ISheet
from mock import patch
from pyramid import testing

import pytest
import zope.interface
import unittest


#############
#  helpers  #
#############

class InterfaceX(zope.interface.Interface):

    """Useless Interface for testing."""


class InterfaceY(zope.interface.Interface):

    """Useless Interface for testing."""


class ISheetX(ISheet):

    """Useless PropertyInterface for testing."""


class ISheetY(ISheet):

    """Useless PropertyInterface for testing."""


class DummyPropertySheetAdapter(object):

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


@patch('substanced.objectmap.ObjectMap', autospec=True)
def make_folder_with_objectmap(dummyobjectmap=None):
    folder = testing.DummyResource()
    folder.__objectmap__ = dummyobjectmap.return_value
    folder.__objectmap__.new_objectid.return_value = 1
    return folder


###########
#  tests  #
###########

class VersionableFubelIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.resources')
        self.config.include('adhocracy.sheets.name')
        self.config.include('adhocracy.sheets.tags')
        self.context = make_folder_with_objectmap()

    def tearDown(self):
        testing.tearDown()

    def make_one(self):
        from . import IFubelVersionsPool
        from . import ResourceFactory
        return ResourceFactory(IFubelVersionsPool)(self.context)

    def test_create(self):
        from . import IVersionableFubel
        from . import ITag
        #_register_dummypropertysheet_adapter(self.config)
        inst = self.make_one()
        fubel = inst['VERSION_0000000']
        fubel_oid = fubel.__oid__
        first = inst['FIRST']
        last = inst['LAST']
        assert IVersionableFubel.providedBy(fubel)
        assert ITag.providedBy(first)
        assert ITag.providedBy(last)
        wanted = {'adhocracy.sheets.tags.ITag': {'elements': [fubel_oid]},
                  'adhocracy.sheets.name.IName': {'name': 'FIRST'}}
        assert first._propertysheets == wanted
        wanted = {'adhocracy.sheets.tags.ITag': {'elements': [fubel_oid]},
                  'adhocracy.sheets.name.IName': {'name': 'LAST'}}
        assert last._propertysheets == wanted


class ResourceFactoryUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        context = make_folder_with_objectmap()
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

    def test_valid_dotted_resource_iface(self):
        from adhocracy.interfaces import IResource
        from persistent.mapping import PersistentMapping
        from persistent.interfaces import IPersistent
        from zope.interface import directlyProvidedBy
        inst = self.make_one(IResource.__identifier__)
        resource = inst(self.context)

        assert isinstance(resource, PersistentMapping)
        assert IPersistent.providedBy(resource)
        assert IResource in directlyProvidedBy(resource)

    def test_valid_non_dotted_resource_iface(self):
        from adhocracy.interfaces import IResource
        from persistent.mapping import PersistentMapping
        from persistent.interfaces import IPersistent
        from zope.interface import directlyProvidedBy
        inst = self.make_one(IResource)
        resource = inst(self.context)

        assert isinstance(resource, PersistentMapping)
        assert IPersistent.providedBy(resource)
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

    def test_valid_add_oid(self):
        from adhocracy.interfaces import IResource
        inst = self.make_one(IResource)
        resource = inst(self.context)
        assert resource.__oid__ == 1
        assert not hasattr(resource, '__parent__')

    def test_valid_non_add_oid(self):
        from adhocracy.interfaces import IResource
        resource = self.make_one(IResource)(self.context, add_oid=False)
        with pytest.raises(AttributeError):
            resource.__oid__
        assert not hasattr(resource, '__parent__')

    def test_valid_after_create(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        def dummy_after_create(context, registry):
            context.test = 'aftercreate'

        class IResourceType(IResource):
            taggedValue('after_creation', [dummy_after_create])

        resource = ResourceFactory(IResourceType)(self.context)
        assert resource.test == 'aftercreate'

    def test_valid_non_after_create(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        def dummy_after_create(context, registry):
            context.test = 'aftercreate'

        class IResourceType(IResource):
            taggedValue('after_creation', [dummy_after_create])

        resource = ResourceFactory(IResourceType)(self.context,
                                                  run_after_creation=False)
        with pytest.raises(AttributeError):
            resource.test

    def test_valid_with_appstructs_data(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        class IResourceType(IResource):
            taggedValue('basic_sheets', set([ISheetY.__identifier__]))

        data = {ISheetY.__identifier__: {"count": 0}}
        _register_dummypropertysheet_adapter(self.config)

        resource = ResourceFactory(IResourceType)(self.context, appstructs=data)
        assert resource['dummy_appstruct'] == data[ISheetY.__identifier__]

    def test_valid_with_ctructs_data(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        class IResourceType(IResource):
            taggedValue('basic_sheets', set([ISheetY.__identifier__]))

        data = {ISheetY.__identifier__: {"count": 0}}
        _register_dummypropertysheet_adapter(self.config)

        resource = ResourceFactory(IResourceType)(self.context, cstructs=data)
        assert resource['dummy_cstruct'] == data[ISheetY.__identifier__]

    def test_non_valid_missing_context(self):
        from adhocracy.interfaces import IResource
        with pytest.raises(TypeError):
            self.make_one(IResource)()

    def test_non_valid_wrong_iresource_iface(self):
        from adhocracy.resources import ResourceFactory
        from zope.interface import Interface

        class InterfaceY(Interface):
            pass

        with pytest.raises(AssertionError):
            ResourceFactory(InterfaceY)(self.context)

    def test_non_valid_wrong_iproperty_iface(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        class IResourceType(IResource):
            taggedValue('basic_sheets',
                        set([InterfaceY.__identifier__]))

        with pytest.raises(AssertionError):
            ResourceFactory(IResourceType)(self.context)


class ResourceFactoryIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.resources')
        self.config.include('adhocracy.registry')

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        content_types = self.config.registry.content.factory_types
        assert 'adhocracy.resources.IFubel' in content_types
        assert 'adhocracy.resources.IVersionableFubel'\
            in content_types
        assert 'adhocracy.resources.IFubelVersionsPool'\
            in content_types
        assert 'adhocracy.resources.IPool' in content_types

    def test_includeme_registry_create_content(self):
        from adhocracy.resources import IPool
        iresource = IPool
        iresource_id = iresource.__identifier__
        context = make_folder_with_objectmap()
        resource = self.config.registry.content.create(iresource_id, context)
        assert iresource.providedBy(resource)
