from pyramid import testing

import adhocracy.properties.interfaces
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


class IPropertyX(adhocracy.properties.interfaces.IProperty):

    """Useless PropertyInterface for testing"""


class IPropertyY(adhocracy.properties.interfaces.IProperty):

    """Useless PropertyInterface for testing"""


###########
#  tests  #
###########

class ResourceFactoryUnitTest(unittest.TestCase):

    def test_valid_assign_ifaces(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.resources.interfaces import IResource
        from persistent.mapping import PersistentMapping
        from persistent.interfaces import IPersistent
        from zope.interface import taggedValue, providedBy

        class IResourceType(IResource):
            taggedValue("extended_properties_interfaces",
                        set([IPropertyX.__identifier__]))
            taggedValue("basic_properties_interfaces",
                        set([IPropertyY.__identifier__]))

        resource = ResourceFactory(IResourceType)()
        assert isinstance(resource, PersistentMapping)
        resource_ifaces = [x for x in providedBy(resource).interfaces()]
        assert IPersistent in resource_ifaces
        assert IResourceType in resource_ifaces
        assert IPropertyX in resource_ifaces
        assert IPropertyY in resource_ifaces

    def test_resourcerfactory_none_valid_wrong_iresource_iface(self):
        from adhocracy.resources import ResourceFactory
        from zope.interface import Interface

        class InterfaceY(Interface):
            pass

        with pytest.raises(AssertionError):
            ResourceFactory(InterfaceY)()

    def test_none_valid_wrong_iproperty_iface(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.resources.interfaces import IResource
        from zope.interface import taggedValue

        class IResourceType(IResource):
            taggedValue("basic_properties_interfaces",
                        set([InterfaceY.__identifier__]))

        with pytest.raises(AssertionError):
            ResourceFactory(IResourceType)()


class ResourceFactoryIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        self.config.include("substanced.content")
        self.config.include("adhocracy.resources")
        content_types = self.config.registry.content.factory_types
        assert 'adhocracy.resources.interfaces.IFubel' in content_types
        assert 'adhocracy.resources.interfaces.IVersionableFubel'\
            in content_types
        assert 'adhocracy.resources.interfaces.IFubelVersionsPool'\
            in content_types
        assert 'adhocracy.resources.interfaces.IPool' in content_types

    def test_includeme_registry_create_content(self):
        self.config.include("substanced.content")
        self.config.include("adhocracy.resources")
        iresource = adhocracy.resources.interfaces.IPool
        iresource_id = iresource.__identifier__
        resource = self.config.registry.content.create(iresource_id)
        assert iresource.providedBy(resource)
