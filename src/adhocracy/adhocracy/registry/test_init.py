import unittest

from pyramid import testing

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IPool



############
#  helper  #
############

class ISimple(IResource):
    pass

class ISimpleSubtype(ISimple):
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


def _register_content_type(registry, metadata):
    from adhocracy.resources import ResourceFactory
    type = metadata.iresource.__identifier__
    registry.add(type, type, ResourceFactory(metadata))
    registry.meta[type]['resource_metadata'] = metadata


class TestResourceContentRegistry(unittest.TestCase):

    def setUp(self):
        from adhocracy.interfaces import resource_meta
        self.config = testing.setUp()
        self.resource_meta = resource_meta._replace(
            iresource=IResource,
            content_class=testing.DummyResource)

    def tearDown(self):
        testing.tearDown()

    def _make_one(self, registry=None):
        from adhocracy.registry import ResourceContentRegistry
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
        _register_content_type(inst, self.resource_meta)
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
        resource_meta = self.resource_meta._replace(basic_sheets=[ISheet])
        _register_content_type(inst, resource_meta)
        meta = inst.sheets_metadata()
        assert ISheet.__identifier__ in meta
        assert meta[ISheet.__identifier__] == get_all_taggedvalues(ISheet)

    def test_addables_valid_context_is_not_ipool(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResource)
        _register_content_type(inst, self.resource_meta)

        addables = inst.resource_addables(context, testing.DummyRequest())

        assert addables == {}

    def test_addables_valid_no_addables(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IPool)
        pool_meta = self.resource_meta._replace(iresource=IPool)
        _register_content_type(inst, pool_meta)

        addables = inst.resource_addables(context, testing.DummyRequest())

        assert addables == {}

    def test_addables_valid_with_addables(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IPool)
        pool_meta = self.resource_meta._replace(iresource=IPool,
                                                element_types=[ISimple])
        _register_content_type(inst, pool_meta)
        simple_meta = self.resource_meta._replace(iresource=ISimple)
        _register_content_type(inst, simple_meta)

        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = {ISimple.__identifier__: {'sheets_optional': [],
                                           'sheets_mandatory': []}}
        assert wanted == addables

    def test_addables_valid_with_addables_implicit_inherit(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IPool)
        pool_meta = self.resource_meta._replace(iresource=IPool,
                                                element_types=[ISimple])
        _register_content_type(inst, pool_meta)
        _register_propertysheet_adapter(self.config, IPool)
        simple_meta = self.resource_meta._replace(iresource=ISimple)
        _register_content_type(inst, simple_meta)
        simple_sub_meta = self.resource_meta._replace(iresource=ISimpleSubtype,
                                                      is_implicit_addable=True)
        _register_content_type(inst, simple_sub_meta)

        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = [ISimple.__identifier__, ISimpleSubtype.__identifier__]
        assert sorted([x for x in addables.keys()]) == wanted

    def test_addables_valid_with_addables_with_sheets(self):
        inst = self._make_one(self.config.registry)
        context = testing.DummyResource(__provides__=IPool)
        pool_meta = self.resource_meta._replace(iresource=IPool,
                                                element_types=[ISimple])

        simple_meta = self.resource_meta._replace(iresource=ISimple,
                                                  basic_sheets=[ISheetA,
                                                                ISheet])
        _register_content_type(inst, pool_meta)
        _register_content_type(inst, simple_meta)
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
