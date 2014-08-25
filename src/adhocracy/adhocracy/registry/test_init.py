from copy import deepcopy
from pytest import fixture

from pyramid import testing

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IPool


class ISimple(IResource):
    pass


class ISimpleSubtype(ISimple):
    pass


class ISheetA(ISheet):
    pass


def add_resource_meta(request, *metas):
    resource_metas = {}
    for meta in metas:
        iresource = meta.iresource
        resource_metas[iresource.__identifier__] = meta
    request.registry.content.resources_meta = resource_metas


def register_and_add_sheet(context, registry, mock_sheet):
    from zope.interface import alsoProvides
    from adhocracy.interfaces import IResourceSheet
    isheet = mock_sheet.meta.isheet
    alsoProvides(context, isheet)
    registry.registerAdapter(lambda x: mock_sheet, (isheet,),
                             IResourceSheet,
                             isheet.__identifier__)


class TestResourceContentRegistryResourceSheets:

    @fixture
    def request(self, registry, mock_resource_registry):
        request = testing.DummyRequest(registry=registry)
        request.registry.content = mock_resource_registry
        return request

    def _call_fut(self, context, request, **kwargs):
        from adhocracy.registry import ResourceContentRegistry
        mock_registry = request.registry.content
        return ResourceContentRegistry.resource_sheets(
            mock_registry, context, request, **kwargs)

    def test_sheets_without_sheets(self, context, request):
        assert self._call_fut(context, request) == {}

    def test_sheets_with_sheets(self, context, request, mock_sheet):
        register_and_add_sheet(context, request.registry, mock_sheet)
        sheets = self._call_fut(context, request)
        assert sheets[ISheet.__identifier__].meta.isheet == ISheet

    def test_sheets_with_sheets_onlyviewable_readable(self, context, request, mock_sheet):
        register_and_add_sheet(context, request.registry, mock_sheet)
        sheets = self._call_fut(context, request, onlyviewable=True)
        assert ISheet.__identifier__ in sheets

    def test_sheets_with_sheets_onlyviewable_no_permission(self, context, request, mock_sheet, config):
        register_and_add_sheet(context, request.registry, mock_sheet)
        config.testing_securitypolicy(userid='reader', permissive=False)
        assert self._call_fut(context, request, onlyviewable=True) == {}

    def test_sheets_with_sheets_onlyviewable_not_readable(self, context, request, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(readable=False)
        register_and_add_sheet(context, request.registry, mock_sheet)
        assert self._call_fut(context, request, onlyviewable=True) == {}

    def test_sheets_with_sheets_onlyeditable_editable(self, context, request, mock_sheet):
        register_and_add_sheet(context, request.registry, mock_sheet)
        sheets = self._call_fut(context, request, onlyeditable=True)
        assert ISheet.__identifier__ in sheets

    def test_sheets_with_sheets_onlyeditable_no_permission(self, context, request, mock_sheet, config):
        register_and_add_sheet(context, request.registry, mock_sheet)
        config.testing_securitypolicy(userid='reader', permissive=False)
        assert self._call_fut(context, request, onlyeditable=True) == {}

    def test_sheets_with_sheets_onlyeditable_not_readable(self, context, request, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(editable=False)
        register_and_add_sheet(context, request.registry, mock_sheet)
        assert self._call_fut(context, request, onlyeditable=True) == {}

    def test_sheets_with_sheets_onlycreatable_creatable(self, context, request, mock_sheet):
        register_and_add_sheet(context, request.registry, mock_sheet)
        sheets = self._call_fut(context, request, onlycreatable=True)
        assert ISheet.__identifier__ in sheets

    def test_sheets_with_sheets_onlycreatable_no_permission(self, context, request, mock_sheet, config):
        config.testing_securitypolicy(userid='reader', permissive=False)
        register_and_add_sheet(context, request.registry, mock_sheet)
        assert self._call_fut(context, request, onlycreatable=True) == {}

    def test_sheets_with_sheets_onlcreatable_not_createable(self, context, request, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(creatable=False)
        register_and_add_sheet(context, request.registry, mock_sheet)
        assert self._call_fut(context, request, onlycreatable=True) == {}

    def test_sheets_with_sheets_onlymandatory_createmandatory(self, context, request, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(create_mandatory=True)
        register_and_add_sheet(context, request.registry, mock_sheet)
        sheets = self._call_fut(context, request, onlymandatorycreatable=True)
        assert ISheet.__identifier__ in sheets

    def test_sheets_with_sheets_onlymandatory_not_createmandatory(self, context, request, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(create_mandatory=False)
        register_and_add_sheet(context, request.registry, mock_sheet)
        sheets = self._call_fut(context, request, onlymandatorycreatable=True)
        assert sheets == {}


class TestResourceContentRegistry:

    def _make_one(self, registry):
        from adhocracy.registry import ResourceContentRegistry
        return ResourceContentRegistry(registry)

    def test_create(self):
        registry = object()
        inst = self._make_one(registry)
        assert inst.registry == registry
        assert inst.sheets_meta == {}
        assert inst.resources_meta == {}


class TestResourceContentRegistryResourceAddables:

    @fixture
    def request(self, registry, mock_resource_registry):
        request = testing.DummyRequest(registry=registry)
        request.registry.content = mock_resource_registry
        return request

    @fixture
    def pool(self, context, request):
        return testing.DummyResource(__provides__=IPool)

    def _call_fut(self, context, request):
        from adhocracy.registry import ResourceContentRegistry
        mock_registry = request.registry.content
        return ResourceContentRegistry.resource_addables(
            mock_registry, context, request)

    def test_addables_valid_context_is_no_iresource(self, request):
        assert self._call_fut(object(), request) == {}

    def test_addables_valid_context_is_no_ipool(self, context, request, resource_meta):
        add_resource_meta(request, resource_meta)
        assert self._call_fut(context, request) == {}

    def test_addables_valid_no_addables(self, pool, request, resource_meta):
        add_resource_meta(request, resource_meta._replace(iresource=IPool))
        assert self._call_fut(pool, request) == {}

    def test_addables_valid_with_addables(self, pool, request, resource_meta):
        add_resource_meta(request,
                          resource_meta._replace(iresource=IPool, element_types=[ISimple]),
                          resource_meta._replace(iresource=ISimple))
        result = self._call_fut(pool, request)
        assert result == {ISimple.__identifier__: {'sheets_optional': [],
                                                   'sheets_mandatory': []}}

    def test_addables_valid_with_addables_implicit_inherit(self, pool, request, resource_meta):
        add_resource_meta(request,
                          resource_meta._replace(iresource=IPool, element_types=[ISimple]),
                          resource_meta._replace(iresource=ISimple, is_implicit_addable=True),
                          resource_meta._replace(iresource=ISimpleSubtype, is_implicit_addable=True))
        result = self._call_fut(pool, request)
        assert sorted(result.keys()) == [ISimple.__identifier__,
                                         ISimpleSubtype.__identifier__]

    def test_addables_valid_with_addables_with_sheets(self, pool, request, resource_meta, mock_sheet):
        add_resource_meta(request,
                          resource_meta._replace(iresource=IPool, element_types=[ISimple]),
                          resource_meta._replace(iresource=ISimple,
                                                 basic_sheets=[ISheetA, ISheet]))
        mock_sheet.meta = mock_sheet.meta._replace(create_mandatory=False)
        mock_sheeta = deepcopy(mock_sheet)
        mock_sheeta.meta = mock_sheeta.meta._replace(create_mandatory=True)
        request.registry.content.resource_sheets.return_value =\
            {ISheet.__identifier__: mock_sheet,
             ISheetA.__identifier__: mock_sheeta}

        result = self._call_fut(pool, request)

        assert result == {ISimple.__identifier__: {
                          'sheets_optional': [ISheet.__identifier__],
                          'sheets_mandatory': [ISheetA.__identifier__]}}


class TestResourceContentRegistyIncludeme:

    def test_includeme(self, config):
        from adhocracy.registry import includeme
        from adhocracy.registry import ResourceContentRegistry
        config.include('substanced.content')
        config.commit()
        includeme(config)
        isinstance(config.registry.content, ResourceContentRegistry)
