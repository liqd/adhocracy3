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


class DummySheet:

    _data = {}

    def __init__(self, metadata, context):
        self.meta = metadata
        self.context = context

    def set(self, appstruct):
        self._data.update(appstruct)

    def get(self):
        return self._data


def _create_and_register_dummy_sheet(context, isheet):
    from pyramid.threadlocal import get_current_registry
    from zope.interface import alsoProvides
    from adhocracy.interfaces import IResourceSheet
    from adhocracy.interfaces import sheet_metadata
    registry = get_current_registry(context)
    metadata = sheet_metadata._replace(isheet=isheet)
    alsoProvides(context, isheet)
    sheet = DummySheet(metadata, context)
    registry.registerAdapter(lambda x: sheet, (isheet,),
                             IResourceSheet,
                             isheet.__identifier__)
    return sheet


def _add_resource_type_to_registry(metadata, resource_registry):
    from adhocracy.resources import ResourceFactory
    iresource = metadata.iresource
    resource_registry.add(iresource.__identifier__,
                          iresource.__identifier__,
                          ResourceFactory(metadata),
                          resource_metadata=metadata,
                          )


class TestResourceContentRegistry(unittest.TestCase):

    def setUp(self):
        from adhocracy.interfaces import resource_metadata

        self.config = testing.setUp()
        self.resource_meta = resource_metadata._replace(
            iresource=IResource,
            content_class=testing.DummyResource)

    def tearDown(self):
        testing.tearDown()

    def _make_one(self):
        from adhocracy.registry import ResourceContentRegistry
        registry = self.config.registry
        return ResourceContentRegistry(registry)

    def test_sheets_valid_missing_sheets(self):
        inst = self._make_one()
        context = testing.DummyResource(__provides__=IResource)
        sheets = inst.resource_sheets(context, None)
        assert sheets == {}

    def test_sheets_valid_with_sheets(self):
        context = testing.DummyResource(__provides__=(IResource, ISheet))
        _create_and_register_dummy_sheet(context, ISheet)
        inst = self._make_one()

        sheets = inst.resource_sheets(context, testing.DummyRequest())

        assert ISheet.__identifier__ in sheets
        assert sheets[ISheet.__identifier__].meta.isheet == ISheet

    def test_sheets_valid_with_sheets_no_permission(self):
        context = testing.DummyResource(__provides__=(IResource, ISheet))
        _create_and_register_dummy_sheet(context, ISheet)
        self.config.testing_securitypolicy(userid='reader', permissive=False)
        inst = self._make_one()

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyviewable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_no_permission(self):
        context = testing.DummyResource(__provides__=(IResource, ISheet))
        _create_and_register_dummy_sheet(context, ISheet)
        self.config.testing_securitypolicy(userid='reader', permissive=False)
        inst = self._make_one()

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyeditable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_readonly(self):
        context = testing.DummyResource(__provides__=(IResource, ISheet))
        sheet = _create_and_register_dummy_sheet(context, ISheet)
        sheet.meta = sheet.meta._replace(readonly=True,
                                         createmandatory=True)
        inst = self._make_one()

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlyeditable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlymandatory_no_createmandatory(self):
        context = testing.DummyResource(__provides__=(IResource, ISheet))
        _create_and_register_dummy_sheet(context, ISheet)
        inst = self._make_one()

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlymandatorycreatable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlymandatory_with_createmandatory(self):
        context = testing.DummyResource(__provides__=(IResource, ISheet))
        sheet = _create_and_register_dummy_sheet(context, ISheet)
        sheet.meta = sheet.meta._replace(readonly=False,
                                         createmandatory=True)
        inst = self._make_one()

        sheets = inst.resource_sheets(context, testing.DummyRequest(),
                                      onlymandatorycreatable=True)
        assert ISheet.__identifier__ in sheets

    def test_resources_metadata_without_content_type(self):
        inst = self._make_one()
        wanted = inst.resources_metadata()
        assert wanted == {}

    def test_resources_metadata_with_non_iresource_content_types(self):
        inst = self._make_one()
        inst.add("wrong", "wrong", lambda x: x)
        wanted = inst.resources_metadata()
        assert wanted == {}

    def test_resources_metadata_with_resources(self):
        inst = self._make_one()
        _add_resource_type_to_registry(self.resource_meta, inst)
        resources = inst.resources_metadata()
        assert len(resources) == 1
        assert 'iface' in resources[IResource.__identifier__]
        assert 'name' in resources[IResource.__identifier__]
        assert 'metadata' in resources[IResource.__identifier__]

    def test_sheets_metadata_without_resources(self):
        inst = self._make_one()
        wanted = inst.sheets_metadata()
        assert wanted == {}

    def test_sheets_metadata_with_resources(self):
        inst = self._make_one()
        context = testing.DummyResource()
        sheet = _create_and_register_dummy_sheet(context, ISheet)
        resource_meta = self.resource_meta._replace(basic_sheets=[ISheet])
        _add_resource_type_to_registry(resource_meta, inst)
        resources = inst.sheets_metadata()
        assert ISheet.__identifier__ in resources
        assert resources[ISheet.__identifier__] == sheet.meta

    def test_addables_valid_context_is_not_ipool(self):
        inst = self._make_one()
        _add_resource_type_to_registry(self.resource_meta, inst)
        context = testing.DummyResource(__provides__=IResource)

        addables = inst.resource_addables(context, testing.DummyRequest())

        assert addables == {}

    def test_addables_valid_no_addables(self):
        inst = self._make_one()
        pool_meta = self.resource_meta._replace(iresource=IPool)
        _add_resource_type_to_registry(pool_meta, inst)
        context = testing.DummyResource(__provides__=IPool)

        addables = inst.resource_addables(context, testing.DummyRequest())

        assert addables == {}

    def test_addables_valid_with_addables(self):
        inst = self._make_one()
        pool_meta = self.resource_meta._replace(iresource=IPool,
                                                element_types=[ISimple])
        _add_resource_type_to_registry(pool_meta, inst)
        simple_meta = self.resource_meta._replace(iresource=ISimple)
        _add_resource_type_to_registry(simple_meta, inst)
        context = testing.DummyResource(__provides__=IPool)

        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = {ISimple.__identifier__: {'sheets_optional': [],
                                           'sheets_mandatory': []}}
        assert wanted == addables

    def test_addables_valid_with_addables_implicit_inherit(self):
        inst = self._make_one()
        pool_meta = self.resource_meta._replace(iresource=IPool,
                                                element_types=[ISimple])
        _add_resource_type_to_registry(pool_meta, inst)
        simple_meta = self.resource_meta._replace(iresource=ISimple,
                                                  is_implicit_addable=True)
        _add_resource_type_to_registry(simple_meta, inst)
        simplesub_meta = self.resource_meta._replace(iresource=ISimpleSubtype,
                                                     is_implicit_addable=True)
        _add_resource_type_to_registry(simplesub_meta, inst)
        context = testing.DummyResource(__provides__=IPool)

        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = [ISimple.__identifier__, ISimpleSubtype.__identifier__]
        assert sorted([x for x in addables.keys()]) == wanted

    def test_addables_valid_with_addables_with_sheets(self):
        inst = self._make_one()
        pool_meta = self.resource_meta._replace(iresource=IPool,
                                                element_types=[ISimple])
        _add_resource_type_to_registry(pool_meta, inst)

        simple_meta = self.resource_meta._replace(iresource=ISimple,
                                                  basic_sheets=[ISheetA,
                                                                ISheet])
        _add_resource_type_to_registry(simple_meta, inst)

        context = testing.DummyResource(__provides__=IPool)
        sheet = _create_and_register_dummy_sheet(context, ISheet)
        sheet.meta = sheet.meta._replace(createmandatory=False)
        sheet_a = _create_and_register_dummy_sheet(context, ISheetA)
        sheet_a.meta = sheet_a.meta._replace(createmandatory=True)

        addables = inst.resource_addables(context, testing.DummyRequest())

        wanted = {ISimple.__identifier__: {
            'sheets_optional': [ISheet.__identifier__],
            'sheets_mandatory': [ISheetA.__identifier__]}}
        assert wanted == addables

    def test_includeme(self):
        from adhocracy.registry import includeme
        from adhocracy.registry import ResourceContentRegistry
        self.config.include('substanced.content')
        self.config.commit()
        includeme(self.config)
        registry = self.config.registry.content
        isinstance(registry, ResourceContentRegistry)
