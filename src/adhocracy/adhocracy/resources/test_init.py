from pyramid import testing

from adhocracy.sheets import ISheet
import pytest
import zope.interface
import unittest


#############
#  helpers  #
#############

class InterfaceX(zope.interface.Interface):

    """Useless Interface for testing"""


class InterfaceY(zope.interface.Interface):

    """Useless Interface for testing"""


class ISheetX(ISheet):

    """Useless PropertyInterface for testing."""


class ISheetY(ISheet):

    """Useless PropertyInterface for testing."""


###########
#  tests  #
###########

class ResourceFactoryUnitTest(unittest.TestCase):

    def test_valid_assign_ifaces(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.interfaces import IResource
        from persistent.mapping import PersistentMapping
        from persistent.interfaces import IPersistent
        from zope.interface import taggedValue, providedBy

        class IResourceType(IResource):
            taggedValue('extended_sheets',
                        set([ISheetX.__identifier__]))
            taggedValue('basic_sheets',
                        set([ISheetY.__identifier__]))

        resource = ResourceFactory(IResourceType)()
        assert isinstance(resource, PersistentMapping)
        resource_ifaces = [x for x in providedBy(resource).interfaces()]
        assert IPersistent in resource_ifaces
        assert IResourceType in resource_ifaces
        assert ISheetX in resource_ifaces
        assert ISheetY in resource_ifaces

    def test_valid_after_create(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        def dummy_after_create(context, registry):
            context.test = 'aftercreate'

        class IResourceType(IResource):
            taggedValue('after_creation', [dummy_after_create])

        resource = ResourceFactory(IResourceType)()
        assert resource.test == 'aftercreate'

    def test_resourcerfactory_none_valid_wrong_iresource_iface(self):
        from adhocracy.resources import ResourceFactory
        from zope.interface import Interface

        class InterfaceY(Interface):
            pass

        with pytest.raises(AssertionError):
            ResourceFactory(InterfaceY)()

    def test_none_valid_wrong_iproperty_iface(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.interfaces import IResource
        from zope.interface import taggedValue

        class IResourceType(IResource):
            taggedValue('basic_sheets',
                        set([InterfaceY.__identifier__]))

        with pytest.raises(AssertionError):
            ResourceFactory(IResourceType)()


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
        resource = self.config.registry.content.create(iresource_id)
        assert iresource.providedBy(resource)
