from adhocracy.resources.interfaces import (
    IResource,
    IPool,
)
from adhocracy.properties.interfaces import IProperty
from pyramid import testing

import unittest
import pytest


############
#  helper  #
############

class IResourceA(IPool):
    pass


class IResourceBA(IResourceA):
    pass


class IResourceB(IPool):
    pass


class IPropertyA(IProperty):
    pass


def _register_propertysheet_adapter(config, context, iproperty):
    from adhocracy.properties import ResourcePropertySheetAdapter
    from adhocracy.interfaces import IResourcePropertySheet
    from adhocracy.properties.interfaces import IIProperty
    from pyramid.interfaces import IRequest
    from zope.interface import alsoProvides
    alsoProvides(iproperty, IIProperty)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (iproperty, IRequest, IIProperty),
                                    IResourcePropertySheet)


def _register_content_type(registry, type):
    registry.add(type, type, object())


class TestResourceContentRegistry(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_one(self, registry=None):
        from . import ResourceContentRegistry
        return ResourceContentRegistry(registry)

    def test_sheets_valid_missing_sheets(self):
        inst = self._make_one(self.config)
        context = testing.DummyResource(__provides__=IResource)
        sheets = inst.resource_sheets(context, None)
        assert sheets == {}

    def test_sheets_valid_with_sheets(self):
        from adhocracy.properties import ResourcePropertySheetAdapter
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, IPropertyA))
        _register_propertysheet_adapter(self.config, context, IPropertyA)

        sheets = inst.resource_sheets(context, testing.DummyRequest())

        assert IPropertyA.__identifier__ in sheets
        assert isinstance(sheets[IPropertyA.__identifier__],
                          ResourcePropertySheetAdapter)

    def test_sheets_valid_with_sheets_no_permission(self):
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, IPropertyA))
        _register_propertysheet_adapter(self.config, context, IPropertyA)
        self.config.testing_securitypolicy(userid='reader', permissive=False)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyviewable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_no_permission(self):
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, IPropertyA))
        _register_propertysheet_adapter(self.config, context, IPropertyA)
        self.config.testing_securitypolicy(userid='reader', permissive=False)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyeditable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_readonly(self):
        inst = self._make_one(self.config.registry)
        IPropertyA.setTaggedValue('readonly', True)
        IPropertyA.setTaggedValue('createmandatory', False)
        context = testing.DummyResource(__provides__=(IResource, IPropertyA))
        _register_propertysheet_adapter(self.config, context, IPropertyA)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyeditable=True)
        assert sheets == {}

    def test_addables_valid_context_is_not_iresource(self):
        inst = self._make_one()
        context = testing.DummyResource()

        with pytest.raises(AssertionError):
            inst.resource_addables(context, testing.DummyRequest())

    def test_addables_valid_context_is_not_ipool(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResource)
        _register_content_type(inst, IResource.__identifier__)

        addables = inst.resource_addables(context, testing.DummyRequest())

        assert addables == {}

    def test_addables_valid_no_addables(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResourceB)
        _register_content_type(inst, IResourceB.__identifier__)
        IResourceB.setTaggedValue('addable_content_interfaces', [])

        addables = inst.resource_addables(context, testing.DummyRequest())

        assert addables == {}

    def test_addables_valid_with_addables(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResourceA)
        _register_content_type(inst, IResourceA.__identifier__)
        _register_content_type(inst, IResourceB.__identifier__)
        IResourceA.setTaggedValue('addable_content_interfaces',
                                  [IResourceB.__identifier__])
        IResourceB.setTaggedValue('basic_properties_interfaces', set())

        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = {IResourceB.__identifier__: {'sheets_optional': [],
                                              'sheets_mandatory': []}}
        assert wanted == addables

    def test_addables_valid_with_addables_implicit_inherit(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResourceA)
        _register_content_type(inst, IResourceA.__identifier__)
        _register_content_type(inst, IResourceBA.__identifier__)
        IResourceA.setTaggedValue('addable_content_interfaces',
                                  [IResourceA.__identifier__])
        IResourceA.setTaggedValue('basic_properties_interfaces', set())
        IResourceBA.setTaggedValue('basic_properties_interfaces', set())
        IResourceBA.setTaggedValue('is_implicit_addable', True)
        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = [IResourceA.__identifier__, IResourceBA.__identifier__]
        assert sorted([x for x in addables.keys()]) == wanted

    def test_addables_valid_with_addables_with_sheets(self):
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=IResourceA)
        _register_content_type(inst, IResourceA.__identifier__)
        _register_content_type(inst, IResourceB.__identifier__)
        IResourceA.setTaggedValue('addable_content_interfaces',
                                  [IResourceB.__identifier__])
        IResourceB.setTaggedValue('basic_properties_interfaces', set([
                                  IPropertyA.__identifier__,
                                  IProperty.__identifier__]))
        IPropertyA.setTaggedValue('createmandatory', True)
        _register_propertysheet_adapter(self.config, context, IProperty)
        _register_propertysheet_adapter(self.config, context, IPropertyA)
        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = {IResourceB.__identifier__: {
            'sheets_optional': [IProperty.__identifier__],
            'sheets_mandatory': [IPropertyA.__identifier__]}}
        assert wanted == addables

    def test_includeme(self):
        from . import includeme
        from . import ResourceContentRegistry
        self.config.include('substanced.content')
        self.config.commit()
        includeme(self.config)
        registry = self.config.registry.content
        isinstance(registry, ResourceContentRegistry)
