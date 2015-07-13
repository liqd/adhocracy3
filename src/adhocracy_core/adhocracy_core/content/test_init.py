from copy import deepcopy
from pytest import fixture
from pytest import raises
from pytest import mark
from unittest.mock import Mock

from pyramid import testing

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IResource


class ISimple(IResource):
    pass


class ISimpleS(ISimple):
    pass


class ISheetA(ISheet):
    pass


class TestResourceContentRegistry:

    @fixture
    def resource_meta(self, resource_meta):
        return resource_meta._replace(basic_sheets=[ISheet])

    @fixture
    def sheet_meta(self, sheet_meta, mock_sheet):
        sheet_meta = sheet_meta._replace(isheet=ISheet,
                                         creatable=True,
                                         create_mandatory=True,
                                         editable=True,
                                         readable=True,
                                         sheet_class=lambda x, y, z: mock_sheet,
                                       )
        mock_sheet.meta = sheet_meta
        return sheet_meta

    @fixture
    def inst(self, resource_meta, sheet_meta):
        inst = self.make_one(None)
        inst.resources_meta = {IResource: resource_meta}
        inst.sheets_meta = {ISheet: sheet_meta}
        return inst

    @fixture
    def request_(self, inst):
        request = testing.DummyRequest()
        request.registry.content = inst
        return request

    @fixture
    def mock_registry(self):
        registry = Mock()
        registry.introspector.get_category.return_value = []
        return registry

    @fixture
    def mock_authpolicy(self, registry):
        from pyramid.interfaces import IAuthenticationPolicy
        from pyramid.interfaces import IAuthorizationPolicy
        policy = Mock()
        registry.registerUtility(policy, IAuthenticationPolicy)
        registry.registerUtility(policy, IAuthorizationPolicy)
        return policy

    def make_one(self, registry):
        from adhocracy_core.content import ResourceContentRegistry
        return ResourceContentRegistry(registry)

    def test_create(self, inst):
        registry = object()
        inst = self.make_one(registry)
        assert inst.registry == registry
        assert inst.sheets_meta == {}
        assert inst.resources_meta == {}
        assert inst.resources_meta_addable == {}
        assert inst.workflows_meta == {}

    def test_sheets_all(self, inst, mock_sheet):
        assert inst.sheets_all == {IResource: [mock_sheet]}

    def test_sheets_create(self, inst, mock_sheet):
        assert inst.sheets_create == {IResource: [mock_sheet]}

    def test_sheets_create_mandatory(self, inst, mock_sheet):
        assert inst.sheets_create_mandatory == {IResource: [mock_sheet]}

    def test_sheets_read(self, inst, mock_sheet):
        assert inst.sheets_read == {IResource: [mock_sheet]}

    def test_sheets_edit(self, inst, mock_sheet):
        assert inst.sheets_edit == {IResource: [mock_sheet]}

    def test_get_sheet_isheet_provided_and_registered(self, inst, sheet_meta):
        from adhocracy_core.sheets import AnnotationRessourceSheet
        context = testing.DummyResource(__provides__=ISheet)
        inst.sheets_meta[ISheet] = sheet_meta._replace(
            sheet_class=AnnotationRessourceSheet)
        sheet = inst.get_sheet(context, ISheet)
        assert sheet.context is context

    def test_get_sheet_isheet_not_provided(self, inst, sheet_meta):
        from adhocracy_core.exceptions import RuntimeConfigurationError
        context = testing.DummyResource()
        inst.sheets_meta[ISheet] = sheet_meta
        with raises(RuntimeConfigurationError):
            inst.get_sheet(context, ISheet)

    def test_get_sheet_isheet_not_registered(self, inst):
        context = testing.DummyResource(__provides__=ISheet)
        del inst.sheets_meta[ISheet]
        with raises(KeyError):
            inst.get_sheet(context, ISheet)

    def test_get_sheets_all(self, inst, context, mock_sheet):
        assert inst.get_sheets_all(context) == [mock_sheet]
        assert mock_sheet.context is context

    def test_get_sheets_read(self, inst, context, mock_sheet):
        assert inst.get_sheets_read(context) == [mock_sheet]
        assert mock_sheet.context is context

    def test_get_sheets_read_with_request_no_permission(self, inst, context,
                                                        config, request_):
        config.testing_securitypolicy(userid='hank', permissive=False)
        assert inst.get_sheets_read(context, request_) == []

    def test_get_sheets_read_with_request_with_permission(
           self, inst, context, config, request_, mock_sheet):
        config.testing_securitypolicy(userid='hank', permissive=True)
        assert inst.get_sheets_read(context, request_) == [mock_sheet]

    def test_get_sheets_edit(self, inst, context, mock_sheet):
        assert inst.get_sheets_edit(context) == [mock_sheet]
        assert mock_sheet.context is context

    def test_get_sheets_edit_with_request_no_permission(self, inst, context,
                                                        config, request_):
        config.testing_securitypolicy(userid='hank', permissive=False)
        assert inst.get_sheets_edit(context, request_) == []

    def test_get_sheets_create(self, inst, context, mock_sheet):
        assert inst.get_sheets_create(context) == [mock_sheet]
        assert mock_sheet.context is context

    def test_get_sheets_create_with_iresource(self, inst, context, mock_sheet):
        inst.sheets_all[ISimple] = [mock_sheet]
        assert inst.get_sheets_create(context, iresource=ISimple) == [mock_sheet]

    def test_get_sheets_create_with_wrong_iresource(self, inst, context):
        with raises(KeyError):
            inst.get_sheets_create(context, iresource=ISimple)

    def test_get_sheets_create_with_request_no_permission(self, inst, context,
                                                          config, request_):
        config.testing_securitypolicy(userid='hank', permissive=False)
        assert inst.get_sheets_create(context, request_) == []

    def test_resources_meta_addable_without_addables(self, inst, resource_meta):
        inst.resources_meta[IResource] = resource_meta
        assert inst.resources_meta_addable[IResource] == []

    def test_resources_meta_addable_with_addables(self, inst, resource_meta):
        simple_meta = deepcopy(resource_meta)._replace(iresource=ISimple)
        inst.resources_meta[ISimple] = simple_meta
        resource_meta = resource_meta._replace(element_types= [ISimple])
        inst.resources_meta[IResource] = resource_meta
        assert inst.resources_meta_addable[IResource] == [simple_meta]

    def test_resources_meta_addable_with_addables_implicit(self, inst,
                                                           resource_meta):
        simple_meta = deepcopy(resource_meta)._replace(iresource=ISimple)
        inst.resources_meta[ISimple] = simple_meta
        simples_meta = deepcopy(resource_meta)._replace(iresource=ISimpleS,
                                                        is_implicit_addable=True)
        inst.resources_meta[ISimpleS] = simples_meta
        resource_meta = resource_meta._replace(element_types= [ISimple])
        inst.resources_meta[IResource] = resource_meta
        assert simple_meta in inst.resources_meta_addable[IResource]
        assert simples_meta in inst.resources_meta_addable[IResource]

    def test_get_resources_meta_addable(
            self, inst, context, request_, resource_meta):
        simple_meta = resource_meta._replace(iresource=ISimple)
        inst.resources_meta_addable = {IResource: [simple_meta]}
        assert inst.get_resources_meta_addable(context, request_) ==\
               [simple_meta]

    def test_get_resources_meta_addable_no_permission(
            self, inst, context, config, request_, resource_meta):
        simple_meta = resource_meta._replace(iresource=ISimple)
        inst.resources_meta_addable = {IResource: [simple_meta]}
        config.testing_securitypolicy(userid='hank', permissive=False)
        assert inst.get_resources_meta_addable(context, request_) == []

    def test_get_resources_meta_addable_only_first_version_exists_has_permission(
            self, inst, item, config, request_, resource_meta, mock_authpolicy):
        from adhocracy_core.interfaces import IItem
        from adhocracy_core.interfaces import IItemVersion
        version0 = testing.DummyResource(__provides__=IItemVersion)
        item['VERSION_0000000'] = version0
        item_meta = resource_meta._replace(iresource=IItem,
                                           permission_create='create_xyz')
        version_meta = resource_meta._replace(iresource=IItemVersion,
                                               permission_create='edit_xyz')
        inst.resources_meta = {IItem: item_meta}
        inst.resources_meta_addable = {IItem: [version_meta]}
        effective_principals = ['authenticated']
        mock_authpolicy.effective_principals.return_value = effective_principals
        mock_authpolicy.permits.return_value = True
        assert inst.get_resources_meta_addable(item, request_) == [version_meta]
        mock_authpolicy.permits.assert_called_once_with(item,
                                                        effective_principals,
                                                        'create_xyz')

    def test_get_resources_meta_addable_only_first_version_exists_no_permission(
            self, inst, item, config, request_, resource_meta, mock_authpolicy):
        from adhocracy_core.interfaces import IItem
        from adhocracy_core.interfaces import IItemVersion
        version0 = testing.DummyResource(__provides__=IItemVersion)
        item['VERSION_0000000'] = version0
        item_meta = resource_meta._replace(iresource=IItem,
                                           permission_create='create_xyz')
        version_meta = resource_meta._replace(iresource=IItemVersion,
                                               permission_create='edit_xyz')
        inst.resources_meta = {IItem: item_meta}
        inst.resources_meta_addable = {IItem: [version_meta]}
        effective_principals = ['authenticated']
        mock_authpolicy.effective_principals.return_value = effective_principals
        mock_authpolicy.permits.return_value = False
        assert inst.get_resources_meta_addable(item, request_) == []
        mock_authpolicy.permits.assert_called_once_with(item,
                                                        effective_principals,
                                                        'create_xyz')

    def test_permissions_resource_permission_create_defined(
            self, inst, resource_meta, mock_registry):
        simple_meta = resource_meta._replace(
            iresource=ISimple,
            permission_create='create_simple')
        inst.registry = mock_registry
        inst.resources_meta[ISimple] = simple_meta
        assert 'create_simple' in inst.permissions

    def test_permissions_sheet_permission_view_defined(
            self, inst, sheet_meta, mock_registry):
        sheet_meta = sheet_meta._replace(permission_view='view_p')
        inst.registry = mock_registry
        inst.sheets_meta[sheet_meta] = sheet_meta
        assert 'view_p' in inst.permissions

    def test_permissions_sheet_permission_edit_defined(
            self, inst, sheet_meta, mock_registry):
        sheet_meta = sheet_meta._replace(permission_edit='edit_p')
        inst.registry = mock_registry
        inst.sheets_meta[sheet_meta] = sheet_meta
        assert 'edit_p' in inst.permissions

    def test_permissions_sheet_permission_create_defined(
            self, inst, sheet_meta, mock_registry):
        sheet_meta = sheet_meta._replace(permission_create='create_p')
        inst.registry = mock_registry
        inst.sheets_meta[sheet_meta] = sheet_meta
        assert 'create_p' in inst.permissions

    def test_permissions_workflow_permission(self, inst, mock_registry):
        from adhocracy_core.workflows.sample import sample_meta
        inst.workflows_meta['sample'] = sample_meta
        inst.registry = mock_registry
        assert 'do_transition' in inst.permissions

    def test_permissions_view_permission(self, inst, mock_registry):
        from pyramid.view import view_config

        permission_name = 'view_xyz'
        mock_introspectable = Mock()
        mock_introspectable.title = permission_name
        inst.registry = mock_registry
        inst.registry.introspector.get_category.return_value \
            = [{'introspectable': mock_introspectable}]

        @view_config(permission=permission_name)
        def test_view_xyz(context, request):
            pass

        assert permission_name in inst.permissions

    def test_get_views_permissions_no_permissions(self, mock_registry):
        mock_registry.introspector.get_category.return_value = None
        inst = self.make_one(mock_registry)
        assert inst._get_views_permissions() == []

    @fixture
    def sheet_meta_a(self, sheet_meta):
        from colander import MappingSchema
        class ASchema(MappingSchema):
            field1 = MappingSchema()
        return sheet_meta._replace(isheet=ISheet,
                                   schema_class=ASchema)

    def test_resolve_with_isheet_field_dotted_string(self, inst, sheet_meta_a):
        node = sheet_meta_a.schema_class()['field1']
        inst.sheets_meta[ISheet] = sheet_meta_a
        field = 'field1'
        dotted = ISheet.__identifier__ + ':' + field
        assert inst.resolve_isheet_field_from_dotted_string(dotted) ==\
            (ISheet, field, node)

    def test_resolve_with_non_dotted_string(self, inst):
        dotted = 'colander'
        with raises(ValueError):
            inst.resolve_isheet_field_from_dotted_string(dotted)

    def test_resolve_with_non_interface_dotted_string(self, inst):
        field = 'field1'
        dotted = 'colander.SchemaNode' + ':' + field
        with raises(ValueError):
            inst.resolve_isheet_field_from_dotted_string(dotted)

    def test_resolve_with_non_isheet_dotted_string(self, inst):
        from zope.interface import Interface
        field = 'field1'
        dotted = Interface.__identifier__ + ':' + field
        with raises(ValueError):
            inst.resolve_isheet_field_from_dotted_string(dotted)

    def test_resolve_with_no_such_class_dotted_string(self, inst):
        field = 'field1'
        dotted = 'colander.NoSuchClass' + ':' + field
        with raises(ValueError):
            inst.resolve_isheet_field_from_dotted_string(dotted)

    def test_resolve_with_isheet_but_wrong_field_dotted_string(self, inst,
                                                               sheet_meta_a):
        isheet = sheet_meta_a.isheet
        field = 'WRONG'
        dotted = isheet.__identifier__ + ':' + field
        with raises(ValueError):
            inst.resolve_isheet_field_from_dotted_string(dotted)

    def test_get_worfklow(self, inst, mock_workflow):
        inst.workflows['sample'] = mock_workflow
        assert inst.get_workflow('sample') == mock_workflow

    def test_get_worfklow_raise_if_wrong_name(self, inst, mock_workflow):
        from adhocracy_core.exceptions import RuntimeConfigurationError
        with raises(RuntimeConfigurationError):
            inst.get_workflow('sample')


@fixture
def integration(config):
    config.include('adhocracy_core.content')


@mark.usefixtures('integration')
def test_includeme_register_pool_sheet(config):
    from adhocracy_core.content import ResourceContentRegistry
    assert isinstance(config.registry.content, ResourceContentRegistry)
