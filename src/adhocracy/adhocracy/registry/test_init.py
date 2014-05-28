import unittest
from mock import patch

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


class TestResourceContentRegistrySheets(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        isheet = ISheet
        self.context = testing.DummyResource(__provides__=(IResource, isheet))
        self.sheet = _create_and_register_dummy_sheet(self.context, isheet)
        self.request = testing.DummyRequest()

    def tearDown(self):
        testing.tearDown()

    def _make_one(self, *args, **kwargs):
        from adhocracy.registry import ResourceContentRegistry
        dummy_registry = object()
        resource_registry = ResourceContentRegistry(dummy_registry)
        return resource_registry.resource_sheets(*args, **kwargs)

    def test_sheets_valid_missing_sheets(self):
        request = None
        context = testing.DummyResource()
        sheets = self._make_one(context, request)
        assert sheets == {}

    def test_sheets_valid_with_sheets(self):
        sheets = self._make_one(self.context, self.request)
        assert ISheet.__identifier__ in sheets
        assert sheets[ISheet.__identifier__].meta.isheet == ISheet

    def test_sheets_valid_with_sheets_no_permission(self):
        self.config.testing_securitypolicy(userid='reader', permissive=False)
        sheets = self._make_one(self.context, self.request, onlyviewable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_no_permission(self):
        self.config.testing_securitypolicy(userid='reader', permissive=False)
        sheets = self._make_one(self.context, self.request, onlyeditable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlyeditable_readonly(self):
        self.sheet.meta = self.sheet.meta._replace(editable=False,
                                                   creatable=False)
        sheets = self._make_one(self.context, self.request, onlyeditable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlycreatable_no_permission(self):
        self.config.testing_securitypolicy(userid='reader', permissive=False)
        sheets = self._make_one(self.context, self.request, onlycreatable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlcreatable_readonly(self):
        self.sheet.meta = self.sheet.meta._replace(editable=False,
                                                   creatable=False)
        sheets = self._make_one(self.context, self.request, onlycreatable=True)
        assert sheets == {}

    def test_sheets_valid_with_sheets_onlcreatable_creatable(self):
        self.sheet.meta = self.sheet.meta._replace(editable=False,
                                                   creatable=True)
        sheets = self._make_one(self.context, self.request, onlycreatable=True)
        assert ISheet.__identifier__ in sheets

    def test_sheets_valid_with_sheets_onlymandatory_with_createmandatory(self):
        self.sheet.meta = self.sheet.meta._replace(create_mandatory=True,
                                                   creatable=True)
        sheets = self._make_one(self.context, self.request,
                                onlymandatorycreatable=True)
        assert ISheet.__identifier__ in sheets

    def test_sheets_valid_with_sheets_onlymandatory_no_createmandatory(self):
        self.sheet.meta = self.sheet.meta._replace(create_mandatory=False)
        sheets = self._make_one(self.context, self.request,
                                onlymandatorycreatable=True)
        assert sheets == {}


class TestResourceContentRegistryResourcesMetadata(unittest.TestCase):

    @patch('adhocracy.registry.ResourceContentRegistry')
    def setUp(self, dummy_registry=None):
        from adhocracy.interfaces import resource_metadata
        self.config = testing.setUp()
        self.resource_registry = dummy_registry.return_value
        self.resource_meta = resource_metadata._replace(iresource=IResource)

    def tearDown(self):
        testing.tearDown()

    def _make_one(self):
        from adhocracy.registry import ResourceContentRegistry
        return ResourceContentRegistry.resources_metadata(
            self.resource_registry)

    def test_resources_metadata_without_content_type(self):
        resources = self._make_one()
        assert resources == {}

    def test_resources_metadata_with_non_iresource_content_types(self):
        self.resource_registry.meta = {"wrong": {}}
        resources = self._make_one()
        assert resources == {}

    def test_resources_metadata_with_resources(self):
        type_id = IResource.__identifier__
        self.resource_registry.meta = \
            {type_id: {'resource_metadata': self.resource_meta}}
        resources = self._make_one()
        assert len(resources) == 1
        assert 'iface' in resources[type_id]
        assert 'name' in resources[type_id]
        assert 'metadata' in resources[type_id]


class TestResourceContentRegistrySheetsMetadata(unittest.TestCase):

    @patch('adhocracy.registry.ResourceContentRegistry')
    def setUp(self, dummy_registry=None):
        from adhocracy.interfaces import resource_metadata
        self.config = testing.setUp()
        self.resource_registry = dummy_registry.return_value
        self.resource_meta = resource_metadata._replace(iresource=IResource)
        self.context = testing.DummyResource()

    def tearDown(self):
        testing.tearDown()

    def _add_resource_metadata(self, metadata):
        type_id = metadata.iresource.__identifier__
        self.resource_registry.resources_metadata.return_value = \
            {type_id: {'name': type_id,
                       'iface': metadata.iresource,
                       'metadata': metadata}}

    def _make_one(self):
        from adhocracy.registry import ResourceContentRegistry
        return ResourceContentRegistry.sheets_metadata(
            self.resource_registry)

    def test_sheets_metadata_without_resources(self):
        sheets = self._make_one()
        assert sheets == {}

    def test_sheets_metadata_with_resources_and_basic_isheets(self):
        sheet = _create_and_register_dummy_sheet(self.context, ISheet)
        resource_meta = self.resource_meta._replace(basic_sheets=[ISheet])
        self._add_resource_metadata(resource_meta)
        sheets = self._make_one()
        assert ISheet.__identifier__ in sheets
        assert sheets[ISheet.__identifier__] == sheet.meta

    def test_sheets_metadata_with_resources_and_extended_isheets(self):
        sheet = _create_and_register_dummy_sheet(self.context, ISheet)
        resource_meta = self.resource_meta._replace(extended_sheets=[ISheet])
        self._add_resource_metadata(resource_meta)
        sheets = self._make_one()
        assert ISheet.__identifier__ in sheets
        assert sheets[ISheet.__identifier__] == sheet.meta


class TestResourceContentRegistryResourceAddables(unittest.TestCase):

    @patch('adhocracy.registry.ResourceContentRegistry')
    def setUp(self, dummy_registry=None):
        from adhocracy.interfaces import resource_metadata
        self.config = testing.setUp()
        self.resource_registry = dummy_registry.return_value
        self.resource_meta = resource_metadata
        self.pool = testing.DummyResource(__provides__=IPool)
        self.request = testing.DummyRequest()

    def tearDown(self):
        testing.tearDown()

    def _add_resource_metadatas(self, metadatas):
        resources = {}
        for metadata in metadatas:
            type_id = metadata.iresource.__identifier__
            resources.update(
                {type_id: {'name': type_id,
                           'iface': metadata.iresource,
                           'metadata': metadata}}
            )
        self.resource_registry.resources_metadata.return_value = resources

    def _make_one(self, *args):
        from adhocracy.registry import ResourceContentRegistry
        return ResourceContentRegistry.resource_addables(
            self.resource_registry, *args)

    def test_addables_valid_context_is_no_iresource(self):
        context = testing.DummyResource()
        addables = self._make_one(context, self.request)
        assert addables == {}

    def test_addables_valid_context_is_no_ipool(self):
        resource_meta = self.resource_meta._replace(iresource=IResource)
        context = testing.DummyResource(__provides__=IResource)
        self._add_resource_metadatas([resource_meta])
        addables = self._make_one(context, self.request)
        assert addables == {}

    def test_addables_valid_no_addables(self):
        pool_meta = self.resource_meta._replace(iresource=IPool)
        self._add_resource_metadatas([pool_meta])
        addables = self._make_one(self.pool, self.request)
        assert addables == {}

    def test_addables_valid_with_addables(self):
        pool_meta = self.resource_meta._replace(iresource=IPool,
                                                element_types=[ISimple])
        simple_meta = self.resource_meta._replace(iresource=ISimple)
        self._add_resource_metadatas([pool_meta, simple_meta])

        addables = self._make_one(self.pool, self.request)

        wanted = {ISimple.__identifier__: {'sheets_optional': [],
                                           'sheets_mandatory': []}}
        assert wanted == addables

    def test_addables_valid_with_addables_implicit_inherit(self):
        pool_meta = self.resource_meta._replace(iresource=IPool,
                                                element_types=[ISimple])
        simple_meta = self.resource_meta._replace(iresource=ISimple,
                                                  is_implicit_addable=True)
        simplesub_meta = self.resource_meta._replace(iresource=ISimpleSubtype,
                                                     is_implicit_addable=True)
        self._add_resource_metadatas([pool_meta, simple_meta, simplesub_meta])

        addables = self._make_one(self.pool, self.request)

        wanted = [ISimple.__identifier__, ISimpleSubtype.__identifier__]
        assert sorted([x for x in addables.keys()]) == wanted

    def test_addables_valid_with_addables_with_sheets(self):
        pool_meta = self.resource_meta._replace(iresource=IPool,
                                                element_types=[ISimple])
        simple_meta = self.resource_meta._replace(iresource=ISimple,
                                                  basic_sheets=[ISheetA,
                                                                ISheet])
        self._add_resource_metadatas([pool_meta, simple_meta])

        sheet = _create_and_register_dummy_sheet(self.pool, ISheet)
        sheet.meta = sheet.meta._replace(create_mandatory=False)
        sheet_a = _create_and_register_dummy_sheet(self.pool, ISheetA)
        sheet_a.meta = sheet_a.meta._replace(create_mandatory=True)

        self.resource_registry.resource_sheets.return_value =\
            {ISheet.__identifier__: sheet,
             ISheetA.__identifier__: sheet_a}

        addables = self._make_one(self.pool, self.request)

        wanted = {ISimple.__identifier__: {
            'sheets_optional': [ISheet.__identifier__],
            'sheets_mandatory': [ISheetA.__identifier__]}}
        assert wanted == addables


class ResourceContentRegistyIncludemeUnitTest(unittest.TestCase):

    def setUp(self, dummy_registry=None):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_includeme(self):
        from adhocracy.registry import includeme
        from adhocracy.registry import ResourceContentRegistry
        self.config.include('substanced.content')
        self.config.commit()
        includeme(self.config)
        registry = self.config.registry.content
        isinstance(registry, ResourceContentRegistry)
