from adhocracy.interfaces import ISheet
from adhocracy.resources import IResource
from adhocracy.resources import IPool
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


class ISheetA(ISheet):
    pass


def _register_propertysheet_adapter(config, context, iproperty):
    from adhocracy.sheets import ResourcePropertySheetAdapter
    from adhocracy.interfaces import IResourcePropertySheet
    from zope.interface.interfaces import IInterface
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (iproperty, IInterface),
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
        from adhocracy.sheets import ResourcePropertySheetAdapter
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, context, ISheetA)

        sheets = inst.resource_sheets(context, testing.DummyRequest())

        assert ISheetA.__identifier__ in sheets
        assert isinstance(sheets[ISheetA.__identifier__],
                          ResourcePropertySheetAdapter)

    def test_sheets_valid_with_sheets_no_permission(self):
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, context, ISheetA)
        self.config.testing_securitypolicy(userid='reader', permissive=False)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyviewable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_no_permission(self):
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, context, ISheetA)
        self.config.testing_securitypolicy(userid='reader', permissive=False)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyeditable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_readonly(self):
        inst = self._make_one(self.config.registry)
        ISheetA.setTaggedValue('readonly', True)
        ISheetA.setTaggedValue('createmandatory', False)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, context, ISheetA)

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
        IResourceB.setTaggedValue('basic_sheets', set())

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
        IResourceA.setTaggedValue('basic_sheets', set())
        IResourceBA.setTaggedValue('basic_sheets', set())
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
        IResourceB.setTaggedValue('basic_sheets', set([
                                  ISheetA.__identifier__,
                                  ISheet.__identifier__]))
        ISheetA.setTaggedValue('createmandatory', True)
        _register_propertysheet_adapter(self.config, context, ISheet)
        _register_propertysheet_adapter(self.config, context, ISheetA)
        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = {IResourceB.__identifier__: {
            'sheets_optional': [ISheet.__identifier__],
            'sheets_mandatory': [ISheetA.__identifier__]}}
        assert wanted == addables

    def test_includeme(self):
        from . import includeme
        from . import ResourceContentRegistry
        self.config.include('substanced.content')
        self.config.commit()
        includeme(self.config)
        registry = self.config.registry.content
        isinstance(registry, ResourceContentRegistry)
