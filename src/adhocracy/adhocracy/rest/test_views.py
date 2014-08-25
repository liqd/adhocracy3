"""Test rest.views module."""
from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
import colander
import pytest

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource


class IResourceX(IResource):
    pass


class ISheetB(ISheet):
    pass


class CountSchema(colander.MappingSchema):

    count = colander.SchemaNode(colander.Int(),
                                default=0,
                                missing=colander.drop)


@fixture
def mock_authpolicy(registry):
    from pyramid.interfaces import IAuthenticationPolicy
    from adhocracy.authentication import TokenHeaderAuthenticationPolicy
    policy = Mock(spec=TokenHeaderAuthenticationPolicy)
    registry.registerUtility(policy, IAuthenticationPolicy)
    return policy


@fixture
def mock_password_sheet(registry):
    from adhocracy.interfaces import IResourceSheet
    from adhocracy.sheets.user import IPasswordAuthentication
    from adhocracy.sheets.user import PasswordAuthenticationSheet
    isheet = IPasswordAuthentication
    sheet = Mock(spec=PasswordAuthenticationSheet)
    registry.registerAdapter(lambda x: sheet, (isheet,),
                             IResourceSheet,
                             isheet.__identifier__)
    return sheet


class TestValidateRequest:

    @fixture
    def request(self, cornice_request):
        return cornice_request

    def _make_one(self, context, request, **kw):
        from adhocracy.rest.views import validate_request_data
        validate_request_data(context, request, **kw)

    def test_valid_wrong_method_with_data(self, context, request):
        request.body = '{"wilddata": "1"}'
        request.method = 'wrong_method'
        self._make_one(context, request)
        assert request.validated == {}

    def test_valid_no_schema_with_data(self, context, request):
        request.body = '{"wilddata": "1"}'
        self._make_one(context, request)
        assert request.validated == {}

    def test_valid_with_schema_no_data(self, context, request):
        request.body = ''
        self._make_one(context, request, schema=CountSchema())
        assert request.validated == {}

    def test_valid_with_schema_no_data_empty_dict(self, context, request):
        request.body = '{}'
        self._make_one(context, request, schema=CountSchema())
        assert request.validated == {}

    def test_valid_with_schema_no_data_and_defaults(self, context, request):
        class DefaultDataSchema(colander.MappingSchema):
            count = colander.SchemaNode(colander.Int(),
                                        missing=1)
        request.body = ''
        self._make_one(context, request, schema=DefaultDataSchema())
        assert request.validated == {'count': 1}

    def test_valid_with_schema_with_data(self, context, request):
        request.body = '{"count": "1"}'
        self._make_one(context, request, schema=CountSchema())
        assert request.validated == {'count': 1}

    def test_valid_with_schema_with_data_in_querystring(self, context, request):
        class QueryStringSchema(colander.MappingSchema):
            count = colander.SchemaNode(colander.Int(),
                                        location='querystring')
        request.GET = {'count': 1}
        self._make_one(context, request, schema=QueryStringSchema())
        assert request.validated == {'count': 1}

    def test_non_valid_with_schema_wrong_data(self, context, request):
        from cornice.util import _JSONError
        request.body = '{"count": "wrong_value"}'
        with pytest.raises(_JSONError):
            self._make_one(context, request, schema=CountSchema())
        assert request.errors == [{'location': 'body',
                                   'name': 'count',
                                   'description': '"wrong_value" is not a number'}]

    def test_non_valid_with_schema_wrong_data_cleanup(self, context, request):
        from cornice.util import _JSONError
        request.validated = {'secret_data': 'buh'}
        request.body = '{"count": "wrong_value"}'
        with pytest.raises(_JSONError):
            self._make_one(context, request, schema=CountSchema())
        assert request.validated == {}

    def test_valid_with_extra_validator(self, context, request):
        def validator1(context, request):
            request.validated = {"validator": "1"}
        self._make_one(context, request, extra_validators=[validator1])
        assert request.validated == {"validator": "1"}

    def test_valid_with_extra_validator_and_wrong_schema_data(self, context, request):
        from cornice.util import _JSONError
        def validator1(context, request):
            request._validator_called = True
        request.body = '{"count": "wrong"}'
        with pytest.raises(_JSONError):
            self._make_one(context, request, schema=CountSchema(),
                           extra_validators=[validator1])
        assert hasattr(request, '_validator_called') is False

    def test_valid_with_sequence_schema(self, context, request):
        class TestListSchema(colander.SequenceSchema):
            elements = colander.SchemaNode(colander.String())

        request.body = '["alpha", "beta", "gamma"]'
        self._make_one(context, request, schema=TestListSchema())
        assert request.validated == ['alpha', 'beta', 'gamma']

    def test_with_invalid_sequence_schema(self, context, request):
        class TestListSchema(colander.SequenceSchema):
            elements = colander.SchemaNode(colander.String())
            nonsense_node = colander.SchemaNode(colander.String())

        request.body = '["alpha", "beta", "gamma"]'
        with pytest.raises(colander.Invalid):
            self._make_one(context, request, schema=TestListSchema())
        assert request.validated == {}

    def test_invalid_with_sequence_schema(self, context, request):
        class TestListSchema(colander.SequenceSchema):
            elements = colander.SchemaNode(colander.Integer())

        from cornice.util import _JSONError
        request.body = '[1, 2, "three"]'
        with pytest.raises(_JSONError):
            self._make_one(context, request, schema=TestListSchema())
        assert request.validated == {}

    def test_invalid_with_not_sequence_and_not_mapping_schema(self, context, request):
        schema = colander.SchemaNode(colander.Int())
        with pytest.raises(Exception):
            self._make_one(context, request, schema=schema)


class TestValidatePOSTRootVersions:

    @fixture
    def request(self, cornice_request):
        return cornice_request

    def make_one(self, context, request):
        from adhocracy.rest.views import validate_post_root_versions
        validate_post_root_versions(context, request)

    def test_valid_no_value(self, request, context):
        self.make_one(context, request)
        assert request.errors == []

    def test_valid_empty_value(self, request, context):
        self.make_one(context, request)
        request.validated = {'root_versions': []}
        assert request.errors == []

    def test_valid_with_value(self, request, context):
        from adhocracy.interfaces import IItemVersion
        from adhocracy.interfaces import ISheet
        root = testing.DummyResource(__provides__=(IItemVersion, ISheet))
        context['root'] = root
        request.validated = {'root_versions': ["/root"]}

        self.make_one(context, request)

        assert request.errors == []
        assert request.validated == {'root_versions': [root]}

    def test_non_valid_value_has_wrong_iface(self, request, context):
        from adhocracy.interfaces import ISheet
        root = testing.DummyResource(__provides__=(IResourceX, ISheet))
        context['root'] = root
        request.validated = {'root_versions': ["/root"]}

        self.make_one(context, request)

        assert request.errors != []
        assert request.validated == {'root_versions': []}

    def test_non_valid_value_does_not_exists(self, request, context):
        request.validated = {'root_versions': ["/root"]}
        self.make_one(context, request)
        assert request.errors != []
        assert request.validated == {'root_versions': []}


class TestRESTView:

    @fixture
    def request(self, cornice_request):
        return cornice_request

    def make_one(self, context, request):
        from adhocracy.rest.views import RESTView
        return RESTView(context, request)

    def test_create_valid(self, request, context):
        inst = self.make_one(context, request)
        assert inst.validation_GET == (None, [])
        assert inst.validation_HEAD == (None, [])
        assert inst.validation_OPTIONS == (None, [])
        assert inst.validation_PUT == (None, [])
        assert inst.validation_POST == (None, [])
        assert inst.context is context
        assert inst.request is request
        assert inst.request.errors == []
        assert inst.request.validated == {}


class TestResourceRESTView:


    @fixture
    def request(self, cornice_request, mock_resource_registry):
        cornice_request.registry.content = mock_resource_registry
        return cornice_request

    def make_one(self, context, request):
        from adhocracy.rest.views import ResourceRESTView
        return ResourceRESTView(context, request)

    def test_create_valid(self, request, context):
        from adhocracy.rest.views import RESTView
        inst = self.make_one(context, request)
        assert isinstance(inst, RESTView)
        assert inst.registry is request.registry.content

    def test_options_valid_no_sheets_and_addables(self, request, context):
        from adhocracy.rest.schemas import OPTIONResourceResponseSchema
        inst = self.make_one(context, request)
        response = inst.options()
        wanted = OPTIONResourceResponseSchema().serialize()
        assert wanted == response

    def test_options_valid_with_sheets_and_addables(self, request, context):
        from adhocracy.rest.schemas import OPTIONResourceResponseSchema
        registry = request.registry.content
        registry.resource_sheets.return_value = {'ipropertyx': object()}
        registry.resource_addables.return_value = \
            {'iresourcex': {'sheets_mandatory': [],
                            'sheets_optional': ['ipropertyx']}}

        inst = self.make_one(context, request)
        response = inst.options()

        wanted = OPTIONResourceResponseSchema().serialize()
        wanted['PUT']['request_body'] = {'data': {'ipropertyx': {}}}
        wanted['GET']['response_body']['data']['ipropertyx'] = {}
        wanted['POST']['request_body'] = [{'content_type': 'iresourcex',
                                           'data': {'ipropertyx': {}}}]

        assert wanted == response

    def test_get_valid_no_sheets(self, request, context):
        from adhocracy.rest.schemas import GETResourceResponseSchema

        inst = self.make_one(context, request)
        response = inst.get()

        wanted = GETResourceResponseSchema().serialize()
        wanted['path'] = '/'
        wanted['data'] = {}
        wanted['content_type'] = IResource.__identifier__
        assert wanted == response

    def test_get_valid_with_sheets(self, request, context, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(isheet=ISheetB)
        mock_sheet.get_cstruct.return_value = 'dummy_cstruct'
        request.registry.content.resource_sheets.return_value = {ISheetB.__identifier__: mock_sheet}

        inst = self.make_one(context, request)
        response = inst.get()

        wanted = {ISheetB.__identifier__: 'dummy_cstruct'}
        assert wanted == response['data']


class TestSimpleRESTView:

    @fixture
    def request(self, cornice_request, mock_resource_registry):
        cornice_request.registry.content = mock_resource_registry
        return cornice_request

    def make_one(self, context, request):
        from adhocracy.rest.views import SimpleRESTView
        return SimpleRESTView(context, request)

    def test_create_valid(self, context, request):
        from adhocracy.rest.views import ResourceRESTView
        from adhocracy.rest.schemas import PUTResourceRequestSchema
        inst = self.make_one(context, request)
        assert issubclass(inst.__class__, ResourceRESTView)
        assert inst.validation_PUT == (PUTResourceRequestSchema, [])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_put_valid_no_sheets(self, request, context):
        request.validated = {"content_type": "X", "data": {}}

        inst = self.make_one(context, request)
        response = inst.put()

        wanted = {'path': '/', 'content_type': IResource.__identifier__}
        assert wanted == response

    def test_put_valid_with_sheets(self, request, context, mock_sheet):
        request.registry.content.resource_sheets.return_value = {ISheetB.__identifier__: mock_sheet}
        data = {'content_type': 'X',
                'data': {ISheetB.__identifier__: {'x': 'y'}}}
        request.validated = data

        inst = self.make_one(context, request)
        response = inst.put()

        wanted = {'path': '/', 'content_type': IResource.__identifier__}
        assert wanted == response
        assert mock_sheet.set.call_args[0][0] == {'x': 'y'}


class TestPoolRESTView:

    @fixture
    def request(self, cornice_request, mock_resource_registry):
        cornice_request.registry.content = mock_resource_registry
        return cornice_request

    def make_one(self, context, request):
        from adhocracy.rest.views import PoolRESTView
        return PoolRESTView(context, request)

    def test_create(self, request, context):
        from adhocracy.rest.views import SimpleRESTView
        from adhocracy.rest.schemas import POSTResourceRequestSchema
        inst = self.make_one(context, request)
        assert issubclass(inst.__class__, SimpleRESTView)
        assert inst.validation_POST == (POSTResourceRequestSchema, [])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_post_valid(self, request, context):
        request.root = context
        child = testing.DummyResource(__provides__=IResourceX)
        child.__parent__ = context
        child.__name__ = 'child'
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IResourceX.__identifier__,
                                  'data': {}}
        inst = self.make_one(context, request)
        response = inst.post()

        wanted = {'path': '/child', 'content_type': IResourceX.__identifier__}
        assert wanted == response


class TestItemRESTView:

    @fixture
    def request(self, cornice_request, mock_resource_registry):
        cornice_request.registry.content = mock_resource_registry
        return cornice_request

    def make_one(self, context, request):
        from adhocracy.rest.views import ItemRESTView
        return ItemRESTView(context, request)

    def test_create(self, request, context):
        from adhocracy.rest.views import validate_post_root_versions
        from adhocracy.rest.views import SimpleRESTView
        from adhocracy.rest.schemas import POSTItemRequestSchema
        inst = self.make_one(context, request)
        assert issubclass(inst.__class__, SimpleRESTView)
        assert inst.validation_POST == (POSTItemRequestSchema,
                                        [validate_post_root_versions])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_get_item_with_first_version(self, request, context):
        from zope.interface import directlyProvides
        from adhocracy.interfaces import IItem
        from adhocracy.interfaces import IItemVersion
        directlyProvides(context, IItem)
        context['first'] = testing.DummyResource(__provides__=IItemVersion)

        inst = self.make_one(context, request)

        wanted = {'path': '/', 'data': {},
                  'content_type': IItem.__identifier__,
                  'first_version_path': '/first'}
        assert inst.get() == wanted

    def test_get_item_without_first_version(self, request, context):
        from adhocracy.interfaces import IItem
        context = testing.DummyResource(__provides__=IItem)
        context['non_first'] = testing.DummyResource()

        inst = self.make_one(context, request)

        wanted = {'path': '/', 'data': {},
                  'content_type': IItem.__identifier__,
                  'first_version_path': ''}
        assert inst.get() == wanted

    def test_post_valid(self, request, context):
        request.root = context
        child = testing.DummyResource(__provides__=IResourceX,
                                      __parent__=context,
                                      __name__='child')
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IResourceX.__identifier__,
                                  'data': {}}
        inst = self.make_one(context, request)
        response = inst.post()

        wanted = {'path': '/child', 'content_type': IResourceX.__identifier__}
        request.registry.content.create.assert_called_with(IResourceX.__identifier__, context,
                                       creator=None,
                                       appstructs={},
                                       root_versions=[])
        assert wanted == response

    def test_post_valid_item(self, request, context):
        from adhocracy.interfaces import IItem
        from adhocracy.interfaces import IItemVersion
        request.root = context
        child = testing.DummyResource(__provides__=IItem,
                                      __parent__=context,
                                      __name__='child')
        first = testing.DummyResource(__provides__=IItemVersion)
        child['first'] = first
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IItemVersion.__identifier__,
                                  'data': {}}
        inst = self.make_one(context, request)
        response = inst.post()

        wanted = {'path': '/child',
                  'content_type': IItem.__identifier__,
                  'first_version_path': '/child/first'}
        assert wanted == response

    def test_post_valid_itemversion(self, request, context):
        from adhocracy.interfaces import IItemVersion
        request.root = context
        child = testing.DummyResource(__provides__=IItemVersion,
                                      __parent__=context,
                                      __name__='child')
        root = testing.DummyResource(__provides__=IItemVersion)
        request.registry.content.create.return_value = child
        request.validated = {'content_type':
                                      IItemVersion.__identifier__,
                                  'data': {},
                                  'root_versions': [root]}
        inst = self.make_one(context, request)
        response = inst.post()

        wanted = {'path': '/child',
                  'content_type': IItemVersion.__identifier__}
        assert request.registry.content.create.call_args[1]['root_versions'] == [root]
        assert wanted == response


class TestMetaApiView:

    @fixture
    def request(self, cornice_request,  mock_resource_registry):
        cornice_request.registry.content = mock_resource_registry
        return cornice_request

    @fixture
    def resource_meta(self):
        from adhocracy.interfaces import resource_metadata
        return resource_metadata._replace(iresource=IResource)

    @fixture
    def sheet_meta(self):
        from adhocracy.interfaces import sheet_metadata
        return sheet_metadata._replace(isheet=ISheet,
                                       schema_class=colander.MappingSchema)

    def make_one(self, request, context):
        from adhocracy.rest.views import MetaApiView
        return MetaApiView(context, request)

    def test_get_empty(self, request, context):
        inst = self.make_one(request, context)
        response = inst.get()
        assert sorted(response.keys()) == ['resources', 'sheets']
        assert response['resources'] == {}
        assert response['sheets'] == {}

    def test_get_resources(self, request, context, resource_meta):
        metas = {IResource.__identifier__: resource_meta}
        request.registry.content.resources_meta = metas
        inst = self.make_one(request, context)
        resp = inst.get()
        assert IResource.__identifier__ in resp['resources']
        assert resp['resources'][IResource.__identifier__] == {'sheets': []}

    def test_get_resources_with_sheets_meta(self, request, context, resource_meta):
        metas = {IResource.__identifier__: resource_meta._replace(
            basic_sheets=[ISheet],
            extended_sheets=[ISheetB])}
        request.registry.content.resources_meta = metas
        inst = self.make_one(request, context)

        resp = inst.get()['resources']

        wanted_sheets = [ISheet.__identifier__, ISheetB.__identifier__]
        assert wanted_sheets == resp[IResource.__identifier__]['sheets']

    def test_get_resources_with_element_types_metadata(self, request, context, resource_meta):
        metas = {IResource.__identifier__: resource_meta._replace(
            element_types=[IResource, IResourceX])}
        request.registry.content.resources_meta = metas
        inst = self.make_one(request, context)

        resp = inst.get()['resources']

        wanted = [IResource.__identifier__, IResourceX.__identifier__]
        assert wanted == resp[IResource.__identifier__]['element_types']

    def test_get_resources_with_item_type_metadata(self, request, context, resource_meta):
        metas = {IResource.__identifier__: resource_meta._replace(
            item_type=IResourceX)}
        request.registry.content.resources_meta = metas
        inst = self.make_one(request, context)

        resp = inst.get()['resources']

        wanted = IResourceX.__identifier__
        assert wanted == resp[IResource.__identifier__]['item_type']

    def test_get_sheets(self, request, context, sheet_meta):
        metas = {ISheet.__identifier__: sheet_meta}
        request.registry.content.sheets_meta = metas
        inst = self.make_one(request, context)
        response = inst.get()
        assert ISheet.__identifier__ in response['sheets']
        assert 'fields' in response['sheets'][ISheet.__identifier__]
        assert response['sheets'][ISheet.__identifier__]['fields'] == []

    def test_get_sheets_with_field(self, request, context, sheet_meta):
        class SchemaF(colander.MappingSchema):
            test = colander.SchemaNode(colander.Int())
        metas = {ISheet.__identifier__: sheet_meta._replace(schema_class=SchemaF)}
        request.registry.content.sheets_meta = metas
        inst = self.make_one(request, context)

        response = inst.get()['sheets'][ISheet.__identifier__]

        assert len(response['fields']) == 1
        field_metadata = response['fields'][0]
        assert field_metadata['create_mandatory'] is False
        assert field_metadata['readable'] is True
        assert field_metadata['editable'] is True
        assert field_metadata['creatable'] is True
        assert field_metadata['name'] == 'test'
        assert 'valuetype' in field_metadata

    def test_get_sheet_with_readonly_field(self, request, context, sheet_meta):
        class SchemaF(colander.MappingSchema):
            test = colander.SchemaNode(colander.Int(), readonly=True)
        metas = {ISheet.__identifier__: sheet_meta._replace(schema_class=SchemaF)}
        request.registry.content.sheets_meta = metas
        inst = self.make_one(request, context)

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert field_metadata['editable'] is False
        assert field_metadata['creatable'] is False
        assert field_metadata['create_mandatory'] is False

    def test_get_sheets_with_field_colander_noniteratable(self, request, context, sheet_meta):
        class SchemaF(colander.MappingSchema):
            test = colander.SchemaNode(colander.Int())
        metas = {ISheet.__identifier__: sheet_meta._replace(schema_class=SchemaF)}
        request.registry.content.sheets_meta = metas
        inst = self.make_one(request, context)

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert 'containertype' not in field_metadata
        assert field_metadata['valuetype'] == 'Integer'

    def test_get_sheets_with_field_adhocracy_noniteratable(self, request, context, sheet_meta):
        from adhocracy.schema import Name
        class SchemaF(colander.MappingSchema):
            test = colander.SchemaNode(Name())
        metas = {ISheet.__identifier__: sheet_meta._replace(schema_class=SchemaF)}
        request.registry.content.sheets_meta = metas
        inst = self.make_one(request, context)

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert 'containertype' not in field_metadata
        assert field_metadata['valuetype'] == 'adhocracy.schema.Name'

    def test_get_sheets_with_field_adhocracy_referencelist(self, request, context, sheet_meta):
        from adhocracy.interfaces import SheetToSheet
        from adhocracy.schema import ListOfUniqueReferences
        class SchemaF(colander.MappingSchema):
            test = ListOfUniqueReferences(reftype=SheetToSheet)
        metas = {ISheet.__identifier__: sheet_meta._replace(schema_class=SchemaF)}
        request.registry.content.sheets_meta = metas
        inst = self.make_one(request, context)

        sheet_metadata = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = sheet_metadata['fields'][0]
        assert field_metadata['containertype'] == 'list'
        assert field_metadata['valuetype'] == 'adhocracy.schema.AbsolutePath'
        assert field_metadata['targetsheet'] == ISheet.__identifier__

    def test_get_sheets_with_field_adhocracy_back_referencelist(self, request, context, sheet_meta):
        from adhocracy.interfaces import SheetToSheet
        from adhocracy.schema import ListOfUniqueReferences
        SheetToSheet.setTaggedValue('source_isheet', ISheetB)
        class SchemaF(colander.MappingSchema):
            test = ListOfUniqueReferences(reftype=SheetToSheet, backref=True)
        metas = {ISheet.__identifier__: sheet_meta._replace(schema_class=SchemaF)}
        request.registry.content.sheets_meta = metas
        inst = self.make_one(request, context)

        sheet_metadata = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = sheet_metadata['fields'][0]
        assert field_metadata['targetsheet'] == ISheetB.__identifier__

    # FIXME test for single reference


class TestValidateLoginEmail:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry = registry
        cornice_request.validated['email'] = 'user@example.org'
        return cornice_request

    def _call_fut(self, context, request):
        from adhocracy.rest.views import validate_login_email
        return validate_login_email(context, request)

    def test_valid(self, request, context, mock_user_locator):
        user = testing.DummyResource()
        mock_user_locator.get_user_by_email.return_value = user
        self._call_fut(context, request)
        assert request.validated['user'] == user

    def test_invalid(self, request, context, mock_user_locator):
        mock_user_locator.get_user_by_email.return_value = None
        self._call_fut(context, request)
        assert 'user' not in request.validated
        assert 'User doesn\'t exist' in request.errors[0]['description']


class TestValidateLoginNameUnitTest:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry = registry
        cornice_request.validated['name'] = 'user'
        return cornice_request

    def _call_fut(self, context, request):
        from adhocracy.rest.views import validate_login_name
        return validate_login_name(context, request)

    def test_invalid(self, request, context, mock_user_locator):
        mock_user_locator.get_user_by_login.return_value = None
        self._call_fut(context, request)
        assert 'User doesn\'t exist' in request.errors[0]['description']

    def test_valid(self, request, context, mock_user_locator):
        user = testing.DummyResource()
        mock_user_locator.get_user_by_login.return_value = user
        self._call_fut(context, request)
        assert request.validated['user'] == user


class TestValidateLoginPasswordUnitTest:

    @fixture
    def request(self, cornice_request, registry):
        from adhocracy.sheets.user import IPasswordAuthentication
        cornice_request.registry = registry
        user = testing.DummyResource(__provides__=IPasswordAuthentication)
        cornice_request.validated['user'] = user
        cornice_request.validated['password'] = 'lalala'
        return cornice_request

    def _call_fut(self, context, request):
        from adhocracy.rest.views import validate_login_password
        return validate_login_password(context, request)

    def test_valid(self, request, context, mock_password_sheet):
        sheet = mock_password_sheet
        sheet.check_plaintext_password.return_value = True
        self._call_fut(context, request)
        assert request.errors == []

    def test_invalid(self, request, context, mock_password_sheet):
        sheet = mock_password_sheet
        sheet.check_plaintext_password.return_value = False
        self._call_fut(context, request)
        assert 'password is wrong' in request.errors[0]['description']

    def test_invalid_with_ValueError(self, request, context, mock_password_sheet):
        sheet = mock_password_sheet
        sheet.check_plaintext_password.side_effect = ValueError
        self._call_fut(context, request)
        assert 'password is wrong' in request.errors[0]['description']

    def test_user_is_None(self, request, context):
        request.validated['user'] = None
        self._call_fut(context, request)
        assert request.errors == []


class TestLoginUserName:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry=registry
        cornice_request.validated['user'] = testing.DummyResource()
        cornice_request.validated['password'] = 'lalala'
        return cornice_request

    def _make_one(self, request, context):
        from adhocracy.rest.views import LoginUsernameView
        return LoginUsernameView(request, context)

    def test_post_without_token_authentication_policy(self, request, context):
        inst = self._make_one(context, request)
        with pytest.raises(KeyError):
            inst.post()

    def test_post_with_token_authentication_policy(self, request, context, mock_authpolicy):
        mock_authpolicy.remember.return_value = {'X-User-Path': '/user',
                                                 'X-User-Token': 'token'}
        inst = self._make_one(context, request)
        assert inst.post() == {'status': 'success',
                               'user_path': '/user',
                               'user_token': 'token'}


class TestLoginEmailView:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry=registry
        cornice_request.validated['user'] = testing.DummyResource()
        return cornice_request

    def _make_one(self, context, request):
        from adhocracy.rest.views import LoginEmailView
        return LoginEmailView(context, request)

    def test_post_without_token_authentication_policy(self, request, context):
        inst = self._make_one(context, request)
        with pytest.raises(KeyError):
            inst.post()

    def test_post_with_token_authentication_policy(self, request, context, mock_authpolicy):
        mock_authpolicy.remember.return_value = {'X-User-Path': '/user',
                                                 'X-User-Token': 'token'}
        inst = self._make_one(context, request)
        assert inst.post() == {'status': 'success',
                               'user_path': '/user',
                               'user_token': 'token'}


class TestIntegrationIncludeme:

    def test_includeme(self, config):
        """Check that include me runs without errors."""
        config.include('cornice')
        config.include('adhocracy.rest.views')
