from adhocracy.resources.interfaces import (
    IResource,
    IPool,
)
from adhocracy.properties.interfaces import IProperty
from pyramid import testing

import unittest


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


def _register_propertysheet_adapter(config, context, iproperty, adapter):
    from adhocracy.interfaces import IResourcePropertySheet
    from adhocracy.properties.interfaces import IIProperty
    from pyramid.interfaces import IRequest
    from zope.interface import alsoProvides
    alsoProvides(iproperty, IIProperty)
    config.registry.registerAdapter(adapter,
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
        from .registry import ResourceContentRegistry
        return ResourceContentRegistry(registry)

    def test_propertysheets_valid_missing_sheets(self):
        inst = self._make_one(self.config)
        context = testing.DummyResource(__provides__=IResource)
        sheets = inst.resource_propertysheets(context, None)
        assert sheets == {}

    def test_propertysheets_valid_with_sheets(self):
        from adhocracy.properties import ResourcePropertySheetAdapter
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, IPropertyA))
        _register_propertysheet_adapter(self.config, context, IPropertyA,
                                        ResourcePropertySheetAdapter)

        sheets = inst.resource_propertysheets(context, testing.DummyRequest())

        assert IPropertyA.__identifier__ in sheets
        assert isinstance(sheets[IPropertyA.__identifier__],
                          ResourcePropertySheetAdapter)

    def test_propertysheets_valid_with_sheets_check_permission_read(self):
        from adhocracy.properties import ResourcePropertySheetAdapter
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, IPropertyA))
        _register_propertysheet_adapter(self.config, context, IPropertyA,
                                        ResourcePropertySheetAdapter)
        self.config.testing_securitypolicy(userid='reader', permissive=False)

        sheets = inst.resource_propertysheets(context, testing.DummyRequest(),
                                              check_permission_view=True)
        assert sheets == {}

    def test_propertysheets_valid_with_sheets_check_permission_edit(self):
        from adhocracy.properties import ResourcePropertySheetAdapter
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, IPropertyA))
        _register_propertysheet_adapter(self.config, context, IPropertyA,
                                        ResourcePropertySheetAdapter)
        self.config.testing_securitypolicy(userid='reader', permissive=False)

        sheets = inst.resource_propertysheets(context, testing.DummyRequest(),
                                              check_permission_edit=True)
        assert sheets == {}

    def test_addable_types_valid_context_is_not_ipool(self):
        from zope.interface import Interface
        inst = self._make_one()
        context = testing.DummyResource(__provides__=Interface)
        context.__factory_type__ = Interface.__identifier__
        _register_content_type(inst, Interface.__identifier__)

        addables = inst.resource_addable_types(context)

        assert addables == {}

    def test_addable_types_valid_no_addables(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResourceB)
        context.__factory_type__ = IResourceB.__identifier__
        _register_content_type(inst, IResourceB.__identifier__)
        IResourceB.setTaggedValue("addable_content_interfaces", [])

        addables = inst.resource_addable_types(context)

        assert addables == {}

    def test_addable_types_valid_with_addables(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResourceA)
        context.__factory_type__ = IResourceA.__identifier__
        _register_content_type(inst, IResourceA.__identifier__)
        _register_content_type(inst, IResourceB.__identifier__)
        IResourceA.setTaggedValue("addable_content_interfaces",
                                  [IResourceB.__identifier__])
        IResourceB.setTaggedValue("basic_properties_interfaces",
                                  set(["ipropx"]))
        IResourceB.setTaggedValue("extended_properties_interfaces",
                                  set(["ipropy"]))

        addables = inst.resource_addable_types(context)

        wanted = {IResourceB.__identifier__: set(["ipropx", "ipropy"])}
        assert wanted == addables

    def test_addable_types_valid_with_implicit_inherit_addables(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResourceA)
        context.__factory_type__ = IResourceA.__identifier__
        _register_content_type(inst, IResourceA.__identifier__)
        _register_content_type(inst, IResourceBA.__identifier__)
        IResourceA.setTaggedValue("addable_content_interfaces",
                                  [IResourceA.__identifier__])
        IResourceBA.setTaggedValue("is_implicit_addable", True)
        addables = inst.resource_addable_types(context)

        wanted = [IResourceA.__identifier__, IResourceBA.__identifier__]
        assert sorted([x for x in addables.keys()]) == wanted

    def test_addable_types_valid_non_implicit_inherit_addables(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResourceA)
        context.__factory_type__ = IResourceA.__identifier__
        _register_content_type(inst, IResourceA.__identifier__)
        _register_content_type(inst, IResourceBA.__identifier__)
        IResourceA.setTaggedValue("addable_content_interfaces",
                                  [IResourceA.__identifier__])
        IResourceBA.setTaggedValue("is_implicit_addable", False)

        addables = inst.resource_addable_types(context)

        wanted = [IResourceA.__identifier__]
        assert [x for x in addables.keys()] == wanted

    def test_includeme(self):
        from adhocracy.resources.registry import includeme
        from adhocracy.resources.registry import ResourceContentRegistry
        self.config.include("substanced.content")
        self.config.commit()
        includeme(self.config)
        registry = self.config.registry.content
        isinstance(registry, ResourceContentRegistry)
