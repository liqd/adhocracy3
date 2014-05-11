from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IPool
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


class ISimple(IResource):
    pass


class ISheetA(ISheet):
    pass


def _register_propertysheet_adapter(config, isheet):
    from adhocracy.sheets import ResourcePropertySheetAdapter
    from adhocracy.interfaces import IResourcePropertySheet
    from zope.interface.interfaces import IInterface
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (isheet, IInterface),
                                    IResourcePropertySheet)


def _register_content_type(registry, type):
    from adhocracy.resources import ResourceFactory
    registry.add(type, type, ResourceFactory(type))


class TestResourceContentRegistry(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_one(self, registry=None):
        from . import ResourceContentRegistry
        resource_registry = ResourceContentRegistry(registry)
        resource_registry.registry = self.config.registry
        return resource_registry

    def test_sheets_valid_missing_sheets(self):
        inst = self._make_one(self.config)
        context = testing.DummyResource(__provides__=IResource)
        sheets = inst.resource_sheets(context, None)
        assert sheets == {}

    def test_sheets_valid_with_sheets(self):
        from adhocracy.sheets import ResourcePropertySheetAdapter
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, ISheetA)

        sheets = inst.resource_sheets(context, testing.DummyRequest())

        assert ISheetA.__identifier__ in sheets
        assert isinstance(sheets[ISheetA.__identifier__],
                          ResourcePropertySheetAdapter)

    def test_sheets_valid_with_sheets_no_permission(self):
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, ISheetA)
        self.config.testing_securitypolicy(userid='reader', permissive=False)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyviewable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_no_permission(self):
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, ISheetA)
        self.config.testing_securitypolicy(userid='reader', permissive=False)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyeditable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_readonly(self):
        inst = self._make_one(self.config.registry)
        ISheetA.setTaggedValue('readonly', True)
        ISheetA.setTaggedValue('createmandatory', False)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, ISheetA)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyeditable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlymandatory_no_createmandatory(self):
        inst = self._make_one(self.config.registry)
        ISheetA.setTaggedValue('readonly', False)
        ISheetA.setTaggedValue('createmandatory', False)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, ISheetA)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlymandatorycreatable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlymandatory_with_createmandatory(self):
        inst = self._make_one(self.config.registry)
        ISheetA.setTaggedValue('readonly', False)
        ISheetA.setTaggedValue('createmandatory', True)
        context = testing.DummyResource(__provides__=(IResource, ISheetA))
        _register_propertysheet_adapter(self.config, ISheetA)

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlymandatorycreatable=True)
        assert ISheetA.__identifier__ in sheets

    def test_resources_metadata_without_resources(self):
        inst = self._make_one(self.config.registry)
        wanted = inst.resources_metadata()
        assert wanted == {}

    def test_resources_metadata_with_resources(self):
        inst = self._make_one(self.config.registry)
        _register_content_type(inst, IResource.__identifier__)
        meta = inst.resources_metadata()
        assert len(meta) == 1
        assert 'iface' in meta[IResource.__identifier__]
        assert 'name' in meta[IResource.__identifier__]
        assert 'metadata' in meta[IResource.__identifier__]

    def test_sheets_metadata_without_resources(self):
        inst = self._make_one(self.config.registry)
        wanted = inst.sheets_metadata()
        assert wanted == {}

    def test_sheets_metadata_with_resources(self):
        from adhocracy.utils import get_all_taggedvalues
        inst = self._make_one(self.config.registry)
        _register_content_type(inst, IResource.__identifier__)
        IResource.setTaggedValue('basic_sheets', {ISheet})
        meta = inst.sheets_metadata()
        assert ISheet.__identifier__ in meta
        assert meta[ISheet.__identifier__] == get_all_taggedvalues(ISheet)

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
        IResourceB.setTaggedValue('element_types', [])

        addables = inst.resource_addables(context, testing.DummyRequest())

        assert addables == {}

    def test_addables_valid_with_addables(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResourceA)
        _register_content_type(inst, IResourceA.__identifier__)
        _register_content_type(inst, ISimple.__identifier__)
        IResourceA.setTaggedValue('element_types',
                                  [ISimple.__identifier__])
        ISimple.setTaggedValue('basic_sheets', set())

        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = {ISimple.__identifier__: {'sheets_optional': [],
                                           'sheets_mandatory': []}}
        assert wanted == addables

    def test_addables_valid_with_addables_implicit_inherit(self):
        from adhocracy.sheets.pool import IPool
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResourceA)
        _register_content_type(inst, IResourceA.__identifier__)
        _register_content_type(inst, IResourceBA.__identifier__)
        _register_propertysheet_adapter(self.config, IPool)
        IResourceA.setTaggedValue('element_types',
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
        IResourceA.setTaggedValue('element_types',
                                  [ISimple.__identifier__])
        ISimple.setTaggedValue('basic_sheets', {ISheetA.__identifier__,
                                                ISheet.__identifier__})
        _register_content_type(inst, IResourceA.__identifier__)
        _register_content_type(inst, ISimple.__identifier__)
        ISheetA.setTaggedValue('createmandatory', True)
        _register_propertysheet_adapter(self.config, ISheet)
        _register_propertysheet_adapter(self.config, ISheetA)
        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = {ISimple.__identifier__: {
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
