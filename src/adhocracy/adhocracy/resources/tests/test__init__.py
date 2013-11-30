import pytest
import unittest
from zope.interface import (
    taggedValue,
    providedBy,
)


class TestResourceFactory(unittest.TestCase):

    def test_create(self):
        from adhocracy.resources import ResourceFactory
        from persistent.mapping import PersistentMapping
        from adhocracy.resources.interfaces import IResource
        from adhocracy.testing import (InterfaceX, InterfaceY)

        class IResourceType(IResource):
            taggedValue("extended_properties_interfaces",
                        set([InterfaceX.__identifier__]))
            taggedValue("basic_properties_interfaces",
                        set([InterfaceY.__identifier__]))

        resource = ResourceFactory(IResourceType)()
        assert isinstance(resource, PersistentMapping)
        assert(list(providedBy(resource)),
               [IResourceType, InterfaceX, InterfaceY])

    def test_create_fails_with_wrong_ifaces(self):
        from adhocracy.resources import ResourceFactory
        from adhocracy.testing import InterfaceY

        with pytest.raises(AssertionError):
            ResourceFactory(InterfaceY)()
