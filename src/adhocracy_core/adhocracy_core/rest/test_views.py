"""Test rest.views module."""
from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises
import colander
import pytest

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IResource
from adhocracy_core.testing import register_sheet


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
    from adhocracy_core.authentication import TokenHeaderAuthenticationPolicy
    policy = Mock(spec=TokenHeaderAuthenticationPolicy)
    registry.registerUtility(policy, IAuthenticationPolicy)
    return policy


@fixture
def mock_password_sheet(registry_with_content, sheet_meta):
    from adhocracy_core.sheets.principal import IPasswordAuthentication
    from adhocracy_core.sheets.principal import PasswordAuthenticationSheet
    sheet = Mock(spec=PasswordAuthenticationSheet)
    sheet.meta = sheet_meta._replace(isheet=IPasswordAuthentication)
    register_sheet(None, sheet, registry_with_content)
    return sheet


class TestValidateRequest:

    @fixture
    def myrequest(self, cornice_request):
        return cornice_request

    def make_one(self, context, myrequest, **kw):
        from adhocracy_core.rest.views import validate_request_data
        validate_request_data(context, myrequest, **kw)

    def test_valid_wrong_method_with_data(self, context, myrequest):
        myrequest.body = '{"wilddata": "1"}'
        myrequest.method = 'wrong_method'
        self.make_one(context, myrequest)
        assert myrequest.validated == {}

    def test_valid_no_schema_with_data(self, context, myrequest):
        myrequest.body = '{"wilddata": "1"}'
        self.make_one(context, myrequest)
        assert myrequest.validated == {}

    def test_valid_with_schema_no_data(self, context, myrequest):
        myrequest.body = ''
        self.make_one(context, myrequest, schema=CountSchema())
        assert myrequest.validated == {}

    def test_valid_with_schema_no_data_empty_dict(self, context, myrequest):
        myrequest.body = '{}'
        self.make_one(context, myrequest, schema=CountSchema())
        assert myrequest.validated == {}

    def test_valid_with_schema_no_data_and_defaults(self, context, myrequest):
        class DefaultDataSchema(colander.MappingSchema):
            count = colander.SchemaNode(colander.Int(),
                                        missing=1)
        myrequest.body = ''
        self.make_one(context, myrequest, schema=DefaultDataSchema())
        assert myrequest.validated == {'count': 1}

    def test_valid_with_schema_with_data(self, context, myrequest):
        myrequest.body = '{"count": "1"}'
        myrequest.method = 'PUT'
        self.make_one(context, myrequest, schema=CountSchema())
        assert myrequest.validated == {'count': 1}

    def test_valid_with_schema_with_data_in_querystring(self, context,
                                                        myrequest):
        class QueryStringSchema(colander.MappingSchema):
            count = colander.SchemaNode(colander.Int())
        myrequest.GET = {'count': 1}
        self.make_one(context, myrequest, schema=QueryStringSchema())
        assert myrequest.validated == {'count': 1}

    def test_valid_with_schema_with_extra_fields_in_querystring_discarded(
            self, context, myrequest):
        class QueryStringSchema(colander.MappingSchema):
            count = colander.SchemaNode(colander.Int())
        myrequest.GET = {'count': 1, 'extraflag': 'extra value'}
        self.make_one(context, myrequest, schema=QueryStringSchema())
        assert myrequest.validated == {'count': 1}

    def test_valid_with_schema_with_extra_fields_in_querystring_preserved(
            self, context, myrequest):

        class PreservingQueryStringSchema(colander.MappingSchema):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.typ.unknown = 'preserve'
            count = colander.SchemaNode(colander.Int())

        myrequest.GET = {'count': 1, 'extraflag': 'extra value'}
        self.make_one(context, myrequest,
                       schema=PreservingQueryStringSchema())
        assert myrequest.validated == {'count': 1, 'extraflag': 'extra value'}

    def test_valid_multipart_formdata(self, context, myrequest):
        myrequest.content_type = 'multipart/form-data'
        myrequest.method = 'POST'
        myrequest.POST['count'] = '1'
        self.make_one(context, myrequest, schema=CountSchema())
        assert myrequest.validated == {'count': 1}

    def test_non_valid_with_schema_wrong_data(self, context, myrequest):
        from cornice.util import _JSONError
        myrequest.body = '{"count": "wrong_value"}'
        myrequest.method = 'POST'
        with pytest.raises(_JSONError):
            self.make_one(context, myrequest, schema=CountSchema())
        assert myrequest.errors == [{'location': 'body',
                                   'name': 'count',
                                   'description': '"wrong_value" is not a number'}]

    def test_non_valid_with_schema_wrong_data_cleanup(self, context,
                                                      myrequest):
        from cornice.util import _JSONError
        myrequest.validated = {'secret_data': 'buh'}
        myrequest.body = '{"count": "wrong_value"}'
        myrequest.method = 'POST'
        with pytest.raises(_JSONError):
            self.make_one(context, myrequest, schema=CountSchema())
        assert myrequest.validated == {}

    def test_valid_with_extra_validator(self, context, myrequest):
        def validator1(context, myrequest):
            myrequest.validated = {"validator": "1"}
        self.make_one(context, myrequest, extra_validators=[validator1])
        assert myrequest.validated == {"validator": "1"}

    def test_valid_with_extra_validator_and_wrong_schema_data(self, context,
                                                              myrequest):
        from cornice.util import _JSONError
        def validator1(context, myrequest):
            myrequest._validator_called = True
        myrequest.body = '{"count": "wrong"}'
        myrequest.method = 'POST'
        with pytest.raises(_JSONError):
            self.make_one(context, myrequest, schema=CountSchema(),
                           extra_validators=[validator1])
        assert hasattr(myrequest, '_validator_called') is False

    def test_valid_with_sequence_schema(self, context, myrequest):
        class TestListSchema(colander.SequenceSchema):
            elements = colander.SchemaNode(colander.String())

        myrequest.body = '["alpha", "beta", "gamma"]'
        myrequest.method = 'POST'
        self.make_one(context, myrequest, schema=TestListSchema())
        assert myrequest.validated == ['alpha', 'beta', 'gamma']

    def test_valid_with_sequence_schema_in_querystring(self, context,
                                                       myrequest):
        class TestListSchema(colander.SequenceSchema):
            elements = colander.SchemaNode(colander.String())
        self.make_one(context, myrequest, schema=TestListSchema())
        # since this doesn't make much sense, the validator is just a no-op
        assert myrequest.validated == {}

    def test_with_invalid_sequence_schema(self, context, myrequest):
        class TestListSchema(colander.SequenceSchema):
            elements = colander.SchemaNode(colander.String())
            nonsense_node = colander.SchemaNode(colander.String())

        myrequest.body = '["alpha", "beta", "gamma"]'
        myrequest.method = 'POST'
        with pytest.raises(colander.Invalid):
            self.make_one(context, myrequest, schema=TestListSchema())
        assert myrequest.validated == {}

    def test_invalid_with_sequence_schema(self, context, myrequest):
        class TestListSchema(colander.SequenceSchema):
            elements = colander.SchemaNode(colander.Integer())

        from cornice.util import _JSONError
        myrequest.body = '[1, 2, "three"]'
        myrequest.method = 'POST'
        with pytest.raises(_JSONError):
            self.make_one(context, myrequest, schema=TestListSchema())
        assert myrequest.validated == {}

    def test_invalid_with_not_sequence_and_not_mapping_schema(self, context,
                                                              myrequest):
        schema = colander.SchemaNode(colander.Int())
        with pytest.raises(Exception):
            self.make_one(context, myrequest, schema=schema)

    def test_valid_user_headers_and_authenticated_user(
            self, context, myrequest, monkeypatch):
        from unittest.mock import Mock
        from adhocracy_core.rest import views
        myrequest.headers['X-User-Path'] = 2
        myrequest.headers['X-User-Token'] = 3
        monkeypatch.setattr(views, 'get_user', Mock(return_value='user'))
        self.make_one(context, myrequest)
        assert myrequest.validated == {}

    def test_invalid_user_headers_but_no_authenticated_user(self, context,
                                                            myrequest):
        from cornice.util import _JSONError
        myrequest.headers['X-User-Path'] = 2
        myrequest.headers['X-User-Token'] = 3
        with pytest.raises(_JSONError):
            self.make_one(context, myrequest)
        assert myrequest.validated == {}


class TestValidatePOSTRootVersions:

    @fixture
    def request(self, cornice_request):
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import validate_post_root_versions
        validate_post_root_versions(context, request)

    def test_valid_no_value(self, request, context):
        self.make_one(context, request)
        assert request.errors == []

    def test_valid_empty_value(self, request, context):
        self.make_one(context, request)
        request.validated = {'root_versions': []}
        assert request.errors == []

    def test_valid_with_value(self, request, context):
        from adhocracy_core.interfaces import IItemVersion
        from adhocracy_core.interfaces import ISheet
        root = testing.DummyResource(__provides__=(IItemVersion, ISheet))
        request.validated = {'root_versions': [root]}

        self.make_one(context, request)

        assert request.errors == []
        assert request.validated == {'root_versions': [root]}

    def test_non_valid_value_has_wrong_iface(self, request, context):
        from adhocracy_core.interfaces import ISheet
        root = testing.DummyResource(__provides__=(IResourceX, ISheet))
        request.validated = {'root_versions': [root]}

        self.make_one(context, request)

        assert request.errors != []
        assert request.validated == {'root_versions': []}


class TestRESTView:

    @fixture
    def request(self, cornice_request, changelog):
        cornice_request.registry.changelog = changelog
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import RESTView
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

    def test__build_updated_resources_dict_empty(self, request, context):
        inst = self.make_one(context, request)
        result = inst._build_updated_resources_dict()
        assert result == {}

    def test__build_updated_resources_dict_one_resource(
            self, request, context, changelog_meta):
        res = testing.DummyResource()
        request.registry.changelog[res] = changelog_meta._replace(resource=res,
                                                                  created=True)
        inst = self.make_one(context, request)
        result = inst._build_updated_resources_dict()
        assert result == {'created': [res]}

    def test__build_updated_resources_dict_one_resource_two_events(
            self, request, context, changelog_meta):
        res = testing.DummyResource()
        request.registry.changelog[res] = changelog_meta._replace(
            resource=res, created=True, changed_descendants=True)
        inst = self.make_one(context, request)
        result = inst._build_updated_resources_dict()
        assert result == {'changed_descendants': [res], 'created': [res]}

    def test__build_updated_resources_dict_two_resources(
            self, request, context, changelog_meta):
        res1 = testing.DummyResource()
        res2 = testing.DummyResource()
        request.registry.changelog[res1] = \
            changelog_meta._replace(resource=res1, created=True)
        request.registry.changelog[res2] =\
            changelog_meta._replace(resource=res2, created=True)
        inst = self.make_one(context, request)
        result = inst._build_updated_resources_dict()
        assert list(result.keys()) == ['created']
        assert set(result['created']) == {res1, res2}


class TestResourceRESTView:

    @fixture
    def request_(self, cornice_request, mock_content_registry):
        cornice_request.registry.content = mock_content_registry
        return cornice_request

    def make_one(self, context, request_):
        from adhocracy_core.rest.views import ResourceRESTView
        return ResourceRESTView(context, request_)

    def test_create_valid(self, request_, context):
        from adhocracy_core.rest.views import RESTView
        inst = self.make_one(context, request_)
        assert isinstance(inst, RESTView)
        assert inst.registry is request_.registry.content

    def test_create_method_get_and_resource_blocked(self, request_, context):
        from pyramid.httpexceptions import HTTPGone
        request_.method = 'GET'
        context.hidden = True
        with raises(HTTPGone):
            self.make_one(context, request_)

    def test_create_method_head_and_resource_blocked(self, request_, context):
        from pyramid.httpexceptions import HTTPGone
        request_.method = 'HEAD'
        context.hidden = True
        with raises(HTTPGone):
            self.make_one(context, request_)

    def test_create_method_post_and_resource_blocked(self, request_, context):
        from pyramid.httpexceptions import HTTPGone
        request_.method = 'POST'
        context.deleted = True
        with raises(HTTPGone):
            self.make_one(context, request_)

    def test_options_valid_with_sheets_and_addables(
            self, request_, context, resource_meta, mock_sheet):
        registry = request_.registry.content
        registry.get_sheets_edit.return_value = [mock_sheet]
        registry.get_sheets_read.return_value = [mock_sheet]
        registry.get_resources_meta_addable.return_value = [resource_meta]
        registry.get_sheets_create.return_value = [mock_sheet]
        inst = self.make_one(context, request_)

        response = inst.options()

        wanted = \
        {'GET': {'request_body': {},
         'request_querystring': {},
         'response_body': {'content_type': '',
                           'data': {ISheet.__identifier__: {}},
                           'path': ''}},
         'HEAD': {},
         'OPTIONS': {},
         'POST': {'request_body': [{'content_type': IResource.__identifier__,
                                    'data': {ISheet.__identifier__: {}}}],
                  'response_body': {'content_type': '', 'path': ''}},
         'PUT': {'request_body': {'content_type': '',
                                  'data': {ISheet.__identifier__: {}}},
                 'response_body': {'content_type': '', 'path': ''}}}
        assert wanted['GET'] == response['GET']
        assert wanted['POST'] == response['POST']
        assert wanted['PUT'] == response['PUT']
        assert wanted['HEAD'] == response['HEAD']
        assert wanted['OPTIONS'] == response['OPTIONS']

    def test_options_valid_with_sheets_and_addables_but_no_permissons(
            self, config, request_, context, resource_meta, mock_sheet):
        registry = request_.registry.content
        registry.get_sheets_edit.return_value = [mock_sheet]
        registry.get_sheets_read.return_value = [mock_sheet]
        registry.get_resources_meta_addable.return_value = [resource_meta]
        registry.get_sheets_create.return_value = [mock_sheet]
        inst = self.make_one(context, request_)
        config.testing_securitypolicy(userid='hank', permissive=False)

        response = inst.options()

        wanted = {'HEAD': {},
                  'OPTIONS': {}}
        assert wanted == response

    def test_options_valid_without_sheets_and_addables(self, request_, context):
        inst = self.make_one(context, request_)
        response = inst.options()
        wanted = {'HEAD': {},
                  'OPTIONS': {}}
        assert wanted == response

    def test_add_metadata_permissions_info_no_metadata(self, request_, context):
        inst = self.make_one(context, request_)
        d = {'DummySheet': {}}
        inst._add_metadata_edit_permission_info(d)
        assert d == {'DummySheet': {}}

    def test_add_metadata_permissions_info_without_hide_permission(
            self, request_, context):
        from adhocracy_core.sheets.metadata import IMetadata
        request_.has_permission = Mock(return_value=False)
        inst = self.make_one(context, request_)
        d = {IMetadata.__identifier__: {}}
        inst._add_metadata_edit_permission_info(d)
        assert d == {IMetadata.__identifier__: {'deleted': [True, False]}}

    def test_add_metadata_permissions_info_with_hide_permission(
            self, request_, context):
        from adhocracy_core.sheets.metadata import IMetadata
        request_.has_permission = Mock(return_value=True)
        inst = self.make_one(context, request_)
        d = {IMetadata.__identifier__: {}}
        inst._add_metadata_edit_permission_info(d)
        assert d == {IMetadata.__identifier__: {'deleted': [True, False],
                                                'hidden': [True, False]}}

    def test_add_workflow_permissions_info(self, request_, context, mock_sheet,
                                           mock_workflow):
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        mock_workflow.get_next_states.return_value = ['draft']
        mock_sheet.get.return_value = {'workflow': mock_workflow}
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IWorkflowAssignment)
        editable_sheets = [mock_sheet]
        inst = self.make_one(context, request_)
        d = {}
        inst._add_workflow_edit_permission_info(d, editable_sheets)
        assert d ==\
            {IWorkflowAssignment.__identifier__: {'workflow_state': ['draft']}}

    def test_get_valid_no_sheets(self, request_, context):
        from adhocracy_core.rest.schemas import GETResourceResponseSchema

        inst = self.make_one(context, request_)
        response = inst.get()

        wanted = GETResourceResponseSchema().serialize()
        wanted['path'] = request_.application_url + '/'
        wanted['data'] = {}
        wanted['content_type'] = IResource.__identifier__
        assert wanted == response

    def test_get_valid_with_sheets(self, request_, context, mock_sheet):
        mock_sheet.get_cstruct.return_value = {'name': '1'}
        mock_sheet.schema.add(colander.SchemaNode(colander.Int(), name='name'))
        request_.registry.content.get_sheets_read.return_value = [mock_sheet]
        inst = self.make_one(context, request_)
        assert inst.get()['data'][ISheet.__identifier__] == {'name': '1'}


class TestSimpleRESTView:

    @fixture
    def request(self, cornice_request, registry_with_changelog,
                mock_content_registry):
        cornice_request.registry = registry_with_changelog
        cornice_request.registry.content = mock_content_registry
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import SimpleRESTView
        return SimpleRESTView(context, request)

    def test_create_valid(self, context, request):
        from adhocracy_core.rest.views import ResourceRESTView
        from adhocracy_core.rest.schemas import PUTResourceRequestSchema
        inst = self.make_one(context, request)
        assert issubclass(inst.__class__, ResourceRESTView)
        assert inst.validation_PUT == (PUTResourceRequestSchema, [])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_put_valid_no_sheets(self, request, context, mock_sheet):
        request.registry.content.get_sheets_edit.return_value = [mock_sheet]
        request.validated = {"content_type": "X", "data": {}}

        inst = self.make_one(context, request)
        response = inst.put()

        wanted = {'path': request.application_url + '/',
                  'content_type': IResource.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                          'created': [],
                          'modified': [],
                          'removed': []}}
        assert wanted == response

    def test_put_valid_with_sheets(self, request, context, mock_sheet):
        request.registry.content.get_sheets_edit.return_value = [mock_sheet]
        data = {'content_type': 'X',
                'data': {ISheet.__identifier__: {'x': 'y'}}}
        request.validated = data

        inst = self.make_one(context, request)
        response = inst.put()

        wanted = {'path': request.application_url + '/',
                  'content_type': IResource.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert wanted == response
        assert mock_sheet.set.call_args[0][0] == {'x': 'y'}


class TestPoolRESTView:

    @fixture
    def request(self, cornice_request, registry_with_changelog,
                mock_content_registry):
        cornice_request.registry = registry_with_changelog
        cornice_request.registry.content = mock_content_registry
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import PoolRESTView
        return PoolRESTView(context, request)

    def test_create(self, request, context):
        from adhocracy_core.rest.views import SimpleRESTView
        from adhocracy_core.rest.schemas import POSTResourceRequestSchema
        inst = self.make_one(context, request)
        assert issubclass(inst.__class__, SimpleRESTView)
        assert inst.validation_POST == (POSTResourceRequestSchema, [])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_get_valid_no_sheets(self, request, context):
        from adhocracy_core.rest.schemas import GETResourceResponseSchema

        inst = self.make_one(context, request)
        response = inst.get()

        wanted = GETResourceResponseSchema().serialize()
        wanted['path'] = request.application_url + '/'
        wanted['data'] = {}
        wanted['content_type'] = IResource.__identifier__
        assert wanted == response

    def test_get_valid_pool_sheet_with_query_params(self, request, context,
                                                    mock_sheet):
        from adhocracy_core.sheets.pool import IPool
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPool)
        mock_sheet.get_cstruct.return_value = {}
        request.registry.content.get_sheets_read.return_value = [mock_sheet]
        request.validated['param1'] = 1

        inst = self.make_one(context, request)
        response = inst.get()

        assert response['data'] == {IPool.__identifier__: {}}
        assert mock_sheet.get_cstruct.call_args[1] == {'params': {'param1': 1}}

    def test_post_valid(self, request, context):
        request.root = context
        child = testing.DummyResource(__provides__=IResourceX)
        child.__parent__ = context
        child.__name__ = 'child'
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IResourceX, 'data': {}}
        inst = self.make_one(context, request)
        response = inst.post()

        wanted = {'path': request.application_url + '/child/',
                  'content_type': IResourceX.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert wanted == response

    def test_put_valid_no_sheets(self, request, context, mock_sheet):
        request.registry.content.get_sheets_edit.return_value = [mock_sheet]
        request.validated = {"content_type": "X", "data": {}}
        inst = self.make_one(context, request)
        response = inst.put()
        wanted = {'path': request.application_url + '/',
                  'content_type': IResource.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert wanted == response


class TestUsersRESTView:

    @fixture
    def request(self, cornice_request, registry_with_changelog,
                mock_content_registry):
        cornice_request.registry = registry_with_changelog
        cornice_request.registry.content = mock_content_registry
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import UsersRESTView
        return UsersRESTView(context, request)

    def test_create(self, request, context):
        from adhocracy_core.rest.views import PoolRESTView
        inst = self.make_one(context, request)
        assert issubclass(inst.__class__, PoolRESTView)
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_post_valid(self, request, context):
        request.root = context
        # Little cheat to prevent the POST validator from kicking in --
        # we're working with already-validated data here
        request.method = 'OPTIONS'
        child = testing.DummyResource(__provides__=IResourceX,
                                      __parent__=context,
                                      __name__='child')
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IResourceX,
                             'data': {}}
        inst = self.make_one(context, request)
        response = inst.post()

        wanted = {'path': request.application_url + '/child/',
                  'content_type': IResourceX.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        request.registry.content.create.assert_called_with(IResourceX.__identifier__, context,
                                       creator=None,
                                       appstructs={},
                                       request=request,
                                       )
        assert wanted == response


class TestItemRESTView:

    @fixture
    def request(self, cornice_request, mock_content_registry, changelog):
        cornice_request.registry.content = mock_content_registry
        cornice_request.registry.changelog = changelog
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import ItemRESTView
        return ItemRESTView(context, request)

    def test_create(self, request, context):
        from adhocracy_core.rest.views import validate_post_root_versions
        from adhocracy_core.rest.views import SimpleRESTView
        from adhocracy_core.rest.schemas import POSTItemRequestSchema
        inst = self.make_one(context, request)
        assert issubclass(inst.__class__, SimpleRESTView)
        assert inst.validation_POST == (POSTItemRequestSchema,
                                        [validate_post_root_versions])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_get_item_with_first_version(self, request, context):
        from zope.interface import directlyProvides
        from adhocracy_core.interfaces import IItem
        from adhocracy_core.interfaces import IItemVersion
        directlyProvides(context, IItem)
        context['first'] = testing.DummyResource(__provides__=IItemVersion)

        inst = self.make_one(context, request)

        wanted = {'path': request.application_url + '/',  'data': {},
                  'content_type': IItem.__identifier__,
                  'first_version_path': request.application_url + '/first/'}
        assert inst.get() == wanted

    def test_get_item_without_first_version(self, request, context):
        from adhocracy_core.interfaces import IItem
        context = testing.DummyResource(__provides__=IItem)
        context['non_first'] = testing.DummyResource()

        inst = self.make_one(context, request)

        wanted = {'path': request.application_url + '/',  'data': {},
                  'content_type': IItem.__identifier__,
                  'first_version_path': None}
        assert inst.get() == wanted

    def test_post_valid(self, request, context):
        from adhocracy_core.utils import set_batchmode
        set_batchmode(request)
        request.root = context
        # Little cheat to prevent the POST validator from kicking in --
        # we're working with already-validated data here
        request.method = 'OPTIONS'
        child = testing.DummyResource(__provides__=IResourceX,
                                      __parent__=context,
                                      __name__='child')
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IResourceX,
                             'data': {}}
        inst = self.make_one(context, request)
        response = inst.post()

        wanted = {'path': request.application_url + '/child/',
                  'content_type': IResourceX.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        request.registry.content.create.assert_called_with(IResourceX.__identifier__, context,
                                       creator=None,
                                       appstructs={},
                                       root_versions=[],
                                       request=request,
                                       is_batchmode=True)
        assert wanted == response

    def test_post_valid_item(self, request, context):
        from adhocracy_core.interfaces import IItem
        from adhocracy_core.interfaces import IItemVersion
        request.root = context
        child = testing.DummyResource(__provides__=IItem,
                                      __parent__=context,
                                      __name__='child')
        first = testing.DummyResource(__provides__=IItemVersion)
        child['first'] = first
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IItemVersion,
                             'data': {}}
        inst = self.make_one(context, request)
        response = inst.post()

        wanted = {'path': request.application_url + '/child/',
                  'content_type': IItem.__identifier__,
                  'first_version_path': request.application_url + '/child/first/',
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert wanted == response

    def test_post_valid_itemversion(self, request, context):
        from adhocracy_core.interfaces import IItemVersion
        request.root = context
        child = testing.DummyResource(__provides__=IItemVersion,
                                      __parent__=context,
                                      __name__='child')
        root = testing.DummyResource(__provides__=IItemVersion)
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IItemVersion,
                             'data': {},
                             'root_versions': [root]}
        inst = self.make_one(context, request)
        response = inst.post()

        wanted = {'path': request.application_url + '/child/',
                  'content_type': IItemVersion.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert request.registry.content.create.call_args[1]['root_versions'] == [root]
        assert wanted == response

    def test_post_valid_itemversion_batchmode_last_version_in_transaction_exists(
            self, request, context, mock_sheet):
        from adhocracy_core.interfaces import IItemVersion
        context['last_new_version'] = testing.DummyResource(__provides__=
                                                            IItemVersion)
        request.root = context
        request.validated = {'content_type': IItemVersion,
                             'data': {ISheet.__identifier__: {'x':'y'}},
                             'root_versions': [],
                             '_last_new_version_in_transaction':\
                                 context['last_new_version']}
        request.registry.content.get_sheets_create.return_value = [mock_sheet]
        inst = self.make_one(context, request)
        response = inst.post()
        mock_sheet.set.assert_called_with({'x':'y'},
                                          request=request)
        wanted = {'path': request.application_url + '/last_new_version/',
                  'content_type': IItemVersion.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert wanted == response

    def test_put_valid_no_sheets(self, request, context, mock_sheet):
        request.registry.content.get_sheets_edit.return_value = [mock_sheet]
        request.validated = {"content_type": "X", "data": {}}
        inst = self.make_one(context, request)
        response = inst.put()
        wanted = {'path': request.application_url + '/',
                  'content_type': IResource.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert wanted == response


class TestBadgeAssignmentsRESTView:

    @fixture
    def request_(self, cornice_request, registry_with_changelog,
                 mock_content_registry):
        cornice_request.registry = registry_with_changelog
        cornice_request.registry.content = mock_content_registry
        return cornice_request

    @fixture
    def assignment_sheet(self, mock_sheet):
        from copy import deepcopy
        from adhocracy_core.sheets.badge import IBadgeAssignment
        sheet = deepcopy(mock_sheet)
        sheet.meta = sheet.meta._replace(isheet=IBadgeAssignment)
        return sheet

    @fixture
    def mock_get_assignables(self, monkeypatch):
        from adhocracy_core.rest import views
        mock = Mock(spec=views.get_assignable_badges)
        monkeypatch.setattr(views, 'get_assignable_badges', mock)
        return mock

    def make_one(self, context, request_):
        from adhocracy_core.rest.views import BadgeAssignmentsRESTView
        return BadgeAssignmentsRESTView(context, request_)

    def test_create(self, context, request_):
        from adhocracy_core.rest.views import PoolRESTView
        inst = self.make_one(context, request_)
        assert isinstance(inst, PoolRESTView)

    def test_get(self, context, request_):
        inst = self.make_one(context, request_)
        response = inst.get()
        assert response == {'content_type': 'adhocracy_core.interfaces.IResource',
                            'data': {},
                            'path': 'http://example.com/'}

    def test_options_ignore_if_no_postable_resources(self, context, request_):
        inst = self.make_one(context, request_)
        response = inst.options()
        assert response == {'HEAD': {}, 'OPTIONS': {}}

    def test_options_ignore_if_no_postable_assignments_sheets(
            self, request_, context, resource_meta,  mock_sheet):
        registry = request_.registry.content
        registry.get_resources_meta_addable.return_value = [resource_meta]
        registry.get_sheets_create.return_value = [mock_sheet]
        inst = self.make_one(context, request_)
        response = inst.options()
        assert response['POST']['request_body'][0]['data'] ==\
            {'adhocracy_core.interfaces.ISheet': {}}

    def test_options_add_assignable_badges(
            self, request_, context, resource_meta, assignment_sheet,
            mock_get_assignables):
        registry = request_.registry.content
        registry.get_resources_meta_addable.return_value = [resource_meta]
        registry.get_sheets_create.return_value = [assignment_sheet]
        badge = testing.DummyResource()
        mock_get_assignables.return_value = [badge]
        inst = self.make_one(context, request_)
        response = inst.options()
        assert response['POST']['request_body'][0]['data'] ==\
            {'adhocracy_core.sheets.badge.IBadgeAssignment':
                 {'badge': ['http://example.com/']}}

    def test_post_valid(self, request_, context):
        request = request_
        request.root = context
        child = testing.DummyResource(__provides__=IResourceX)
        child.__parent__ = context
        child.__name__ = 'child'
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IResourceX, 'data': {}}
        inst = self.make_one(context, request_)
        response = inst.post()
        wanted = {'path': request.application_url + '/child/',
                  'content_type': IResourceX.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert wanted == response


class TestMetaApiView:

    @fixture
    def request(self, cornice_request,  mock_content_registry):
        cornice_request.registry.content = mock_content_registry
        return cornice_request

    def make_one(self, request, context):
        from adhocracy_core.rest.views import MetaApiView
        return MetaApiView(context, request)

    def test_get_empty(self, request, context):
        inst = self.make_one(request, context)
        response = inst.get()
        assert response['resources'] == {}
        assert response['sheets'] == {}
        assert response['workflows'] == {}

    def test_get_resources(self, request, context, resource_meta):
        request.registry.content.resources_meta[IResource] = resource_meta
        inst = self.make_one(request, context)
        resp = inst.get()
        assert IResource.__identifier__ in resp['resources']
        assert resp['resources'][IResource.__identifier__]['sheets'] == []
        assert resp['resources'][IResource.__identifier__]['super_types'] == []

    def test_get_resources_with_super_types(self, request, context, resource_meta):
        class IResourceBX(IResourceX):
            pass
        resource_meta._replace(iresource=IResourceBX)
        request.registry.content.resources_meta[IResourceBX] = resource_meta
        inst = self.make_one(request, context)
        resp = inst.get()
        assert resp['resources'][IResourceBX.__identifier__]['super_types'] ==\
            [IResourceX.__identifier__]

    def test_get_resources_with_sheets_meta(self, request, context, resource_meta):
        resource_meta = resource_meta._replace(basic_sheets=(ISheet,),
                                               extended_sheets=(ISheetB,))
        request.registry.content.resources_meta[IResource] = resource_meta
        inst = self.make_one(request, context)

        resp = inst.get()['resources']

        wanted_sheets = [ISheet.__identifier__, ISheetB.__identifier__]
        assert wanted_sheets == resp[IResource.__identifier__]['sheets']

    def test_get_resources_with_element_types_metadata(self, request, context, resource_meta):
        resource_meta = resource_meta._replace(element_types=[IResource,
                                                              IResourceX])
        request.registry.content.resources_meta[IResource] = resource_meta
        inst = self.make_one(request, context)

        resp = inst.get()['resources']

        wanted = [IResource.__identifier__, IResourceX.__identifier__]
        assert wanted == resp[IResource.__identifier__]['element_types']

    def test_get_resources_with_item_type_metadata(self, request, context, resource_meta):
        resource_meta = resource_meta._replace(item_type=IResourceX)
        request.registry.content.resources_meta[IResource] = resource_meta
        inst = self.make_one(request, context)

        resp = inst.get()['resources']

        wanted = IResourceX.__identifier__
        assert wanted == resp[IResource.__identifier__]['item_type']

    def test_get_sheets(self, request, context, sheet_meta):
        request.registry.content.sheets_meta[ISheet] = sheet_meta
        inst = self.make_one(request, context)
        response = inst.get()
        assert ISheet.__identifier__ in response['sheets']
        assert 'fields' in response['sheets'][ISheet.__identifier__]
        assert response['sheets'][ISheet.__identifier__]['fields'] == []
        assert response['sheets'][ISheet.__identifier__]['super_types'] == []

    def test_get_sheets_with_super_types(self, request, context, sheet_meta):
        class ISheetBX(ISheetB):
            pass
        sheet_meta = sheet_meta._replace(isheet=ISheetBX)
        request.registry.content.sheets_meta[ISheetBX] = sheet_meta
        inst = self.make_one(request, context)
        response = inst.get()['sheets'][ISheetBX.__identifier__]
        assert response['super_types'] == [ISheetB.__identifier__]

    def test_get_sheets_with_field(self, request, context, sheet_meta):
        class SchemaF(colander.MappingSchema):
            test = colander.SchemaNode(colander.Int())
        sheet_meta = sheet_meta._replace(schema_class=SchemaF)
        request.registry.content.sheets_meta[ISheet] = sheet_meta
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
        sheet_meta = sheet_meta._replace(schema_class=SchemaF)
        request.registry.content.sheets_meta[ISheet] = sheet_meta
        inst = self.make_one(request, context)

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert field_metadata['editable'] is False
        assert field_metadata['creatable'] is False
        assert field_metadata['create_mandatory'] is False

    def test_get_sheets_with_field_colander_noniteratable(self, request, context, sheet_meta):
        class SchemaF(colander.MappingSchema):
            test = colander.SchemaNode(colander.Int())
        sheet_meta = sheet_meta._replace(schema_class=SchemaF)
        request.registry.content.sheets_meta[ISheet] = sheet_meta
        inst = self.make_one(request, context)

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert 'containertype' not in field_metadata
        assert field_metadata['valuetype'] == 'Integer'

    def test_get_sheets_with_field_adhocracy_noniteratable(self, request, context, sheet_meta):
        from adhocracy_core.schema import Name
        class SchemaF(colander.MappingSchema):
            test = colander.SchemaNode(Name())
        sheet_meta = sheet_meta._replace(schema_class=SchemaF)
        request.registry.content.sheets_meta[ISheet] = sheet_meta
        inst = self.make_one(request, context)

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert 'containertype' not in field_metadata
        assert field_metadata['valuetype'] == 'adhocracy_core.schema.Name'

    def test_get_sheets_with_field_adhocracy_referencelist(self, request, context, sheet_meta):
        from adhocracy_core.interfaces import SheetToSheet
        from adhocracy_core.schema import UniqueReferences
        class SchemaF(colander.MappingSchema):
            test = UniqueReferences(reftype=SheetToSheet)
        sheet_meta = sheet_meta._replace(schema_class=SchemaF)
        request.registry.content.sheets_meta[ISheet] = sheet_meta
        inst = self.make_one(request, context)

        sheet_metadata = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = sheet_metadata['fields'][0]
        assert field_metadata['containertype'] == 'list'
        assert field_metadata['valuetype'] == 'adhocracy_core.schema.AbsolutePath'
        assert field_metadata['targetsheet'] == ISheet.__identifier__

    def test_get_sheets_with_field_adhocracy_back_referencelist(self, request, context, sheet_meta):
        from adhocracy_core.interfaces import SheetToSheet
        from adhocracy_core.schema import UniqueReferences
        class BSheetToSheet(SheetToSheet):
            pass
        BSheetToSheet.setTaggedValue('source_isheet', ISheetB)
        class SchemaF(colander.MappingSchema):
            test = UniqueReferences(reftype=BSheetToSheet, backref=True)
        sheet_meta = sheet_meta._replace(schema_class=SchemaF)
        request.registry.content.sheets_meta[ISheet] = sheet_meta
        inst = self.make_one(request, context)

        sheet_metadata = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = sheet_metadata['fields'][0]
        assert field_metadata['targetsheet'] == ISheetB.__identifier__

    def test_get_sheets_with_field_non_generic_or_container(
            self, request, context, sheet_meta):
        from adhocracy_core.schema import Identifier
        class SchemaF(colander.MappingSchema):
            id = Identifier()
        sheet_meta = sheet_meta._replace(schema_class=SchemaF)
        request.registry.content.sheets_meta[ISheet] = sheet_meta
        inst = self.make_one(request, context)
        sheet_metadata = inst.get()['sheets'][ISheet.__identifier__]
        field_metadata = sheet_metadata['fields'][0]
        assert field_metadata['valuetype'] == 'adhocracy_core.schema.Identifier'

    def test_get_sheets_with_sequence_schema_as_node(self, request, context,
                                                     sheet_meta):
        from adhocracy_core.schema import Roles
        class SchemaF(colander.MappingSchema):
            roles = Roles()
        sheet_meta = sheet_meta._replace(schema_class=SchemaF)
        request.registry.content.sheets_meta[ISheet] = sheet_meta
        inst = self.make_one(request, context)
        sheet_metadata = inst.get()['sheets'][ISheet.__identifier__]
        field_metadata = sheet_metadata['fields'][0]
        assert field_metadata['valuetype'] == 'adhocracy_core.schema.Role'
        assert field_metadata['containertype'] == 'list'

    # TODO test for single reference

    def test_get_workflows(self, request, context):
        inst = self.make_one(request, context)
        request.registry.content.workflows_meta['sample'] = {'states': {},
                                                             'transitions': {}}
        workflows_meta = inst.get()['workflows']
        assert workflows_meta == {'sample': {'states_order': [],
                                             'states': {},
                                             'transitions': {}}}


class TestValidateLoginEmail:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry = registry
        cornice_request.validated['email'] = 'user@example.org'
        return cornice_request

    def call_fut(self, context, request):
        from adhocracy_core.rest.views import validate_login_email
        return validate_login_email(context, request)

    def test_valid(self, request, context, mock_user_locator):
        user = testing.DummyResource()
        mock_user_locator.get_user_by_email.return_value = user
        self.call_fut(context, request)
        assert request.validated['user'] == user

    def test_invalid(self, request, context, mock_user_locator):
        mock_user_locator.get_user_by_email.return_value = None
        self.call_fut(context, request)
        assert 'user' not in request.validated
        assert 'User doesn\'t exist' in request.errors[0]['description']


class TestValidateLoginNameUnitTest:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry = registry
        cornice_request.validated['name'] = 'user'
        return cornice_request

    def call_fut(self, context, request):
        from adhocracy_core.rest.views import validate_login_name
        return validate_login_name(context, request)

    def test_invalid(self, request, context, mock_user_locator):
        mock_user_locator.get_user_by_login.return_value = None
        self.call_fut(context, request)
        assert 'User doesn\'t exist' in request.errors[0]['description']

    def test_valid(self, request, context, mock_user_locator):
        user = testing.DummyResource()
        mock_user_locator.get_user_by_login.return_value = user
        self.call_fut(context, request)
        assert request.validated['user'] == user


class TestValidateLoginPasswordUnitTest:

    @fixture
    def request(self, cornice_request, registry_with_content):
        from adhocracy_core.sheets.principal import IPasswordAuthentication
        cornice_request.registry = registry_with_content
        user = testing.DummyResource(__provides__=IPasswordAuthentication)
        cornice_request.validated['user'] = user
        cornice_request.validated['password'] = 'lalala'
        return cornice_request

    def call_fut(self, context, request):
        from adhocracy_core.rest.views import validate_login_password
        return validate_login_password(context, request)

    def test_valid(self, request, context, mock_password_sheet):
        sheet = mock_password_sheet
        sheet.check_plaintext_password.return_value = True
        self.call_fut(context, request)
        assert request.errors == []

    def test_invalid(self, request, context, mock_password_sheet):
        sheet = mock_password_sheet
        sheet.check_plaintext_password.return_value = False
        self.call_fut(context, request)
        assert 'password is wrong' in request.errors[0]['description']

    def test_invalid_with_ValueError(self, request, context, mock_password_sheet):
        sheet = mock_password_sheet
        sheet.check_plaintext_password.side_effect = ValueError
        self.call_fut(context, request)
        assert 'password is wrong' in request.errors[0]['description']

    def test_user_is_None(self, request, context):
        request.validated['user'] = None
        self.call_fut(context, request)
        assert request.errors == []


class TestValidateAccountActiveUnitTest:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry = registry
        return cornice_request

    def call_fut(self, context, request):
        from adhocracy_core.rest.views import validate_account_active
        return validate_account_active(context, request)

    def test_valid(self, request, context):
        user = testing.DummyResource(active=True)
        request.validated['user'] = user
        self.call_fut(context, request)
        assert not request.errors

    def test_invalid(self, request, context):
        user = testing.DummyResource(active=False)
        request.validated['user'] = user
        self.call_fut(context, request)
        assert 'not yet activated' in request.errors[0]['description']

    def test_no_error_added_after_other_errors(self, request, context):
        user = testing.DummyResource(active=False)
        request.validated['user'] = user
        request.errors.add('blah', 'blah', 'blah')
        assert len(request.errors) == 1
        self.call_fut(context, request)
        assert len(request.errors) == 1


class TestLoginUserName:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry = registry
        cornice_request.validated['user'] = testing.DummyResource()
        cornice_request.validated['password'] = 'lalala'
        return cornice_request

    def make_one(self, request, context):
        from adhocracy_core.rest.views import LoginUsernameView
        return LoginUsernameView(request, context)

    def test_post_without_token_authentication_policy(self, request, context):
        inst = self.make_one(context, request)
        with pytest.raises(KeyError):
            inst.post()

    def test_post_with_token_authentication_policy(self, request, context, mock_authpolicy):
        mock_authpolicy.remember.return_value = {'X-User-Path': '/user',
                                                 'X-User-Token': 'token'}
        inst = self.make_one(context, request)
        assert inst.post() == {'status': 'success',
                               'user_path': '/user',
                               'user_token': 'token'}

    def test_options(self, request, context):
        inst = self.make_one(context, request)
        assert inst.options() == {}


class TestLoginEmailView:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry=registry
        cornice_request.validated['user'] = testing.DummyResource()
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import LoginEmailView
        return LoginEmailView(context, request)

    def test_post_without_token_authentication_policy(self, request, context):
        inst = self.make_one(context, request)
        with pytest.raises(KeyError):
            inst.post()

    def test_post_with_token_authentication_policy(self, request, context, mock_authpolicy):
        mock_authpolicy.remember.return_value = {'X-User-Path': '/user',
                                                 'X-User-Token': 'token'}
        inst = self.make_one(context, request)
        assert inst.post() == {'status': 'success',
                               'user_path': '/user',
                               'user_token': 'token'}

    def test_options(self, request, context):
        inst = self.make_one(context, request)
        assert inst.options() == {}



class TestValidateActivationPathUnitTest:

    @fixture
    def _request(self, cornice_request, registry):
        cornice_request.registry = registry
        cornice_request.validated['path'] = '/foo'
        return cornice_request

    @fixture
    def user_with_metadata(self, config):
        from adhocracy_core.sheets.metadata import IMetadata
        config.include('adhocracy_core.content')
        config.include('adhocracy_core.catalog')
        config.include('adhocracy_core.changelog')
        config.include('adhocracy_core.events')
        config.include('adhocracy_core.sheets.metadata')
        user = testing.DummyResource(__provides__=IMetadata)
        user.activate = Mock()
        return user

    def call_fut(self, context, _request):
        from adhocracy_core.rest.views import validate_activation_path
        return validate_activation_path(context, _request)

    def test_valid(self, _request, user_with_metadata, context,
                   mock_user_locator):
        mock_user_locator.get_user_by_activation_path.return_value = \
            user_with_metadata
        self.call_fut(context, _request)
        assert _request.validated['user'] == user_with_metadata
        assert user_with_metadata.activate.called

    def test_not_found(self, _request, context, mock_user_locator):
        mock_user_locator.get_user_by_activation_path.return_value = None
        self.call_fut(context, _request)
        assert 'Unknown or expired activation path' == _request.errors[0][
            'description']

    def test_found_but_expired(self, _request, user_with_metadata, context,
                               mock_user_locator):
        from datetime import datetime
        from datetime import timezone
        from adhocracy_core.sheets.metadata import IMetadata
        from adhocracy_core.utils import get_sheet
        mock_user_locator.get_user_by_activation_path.return_value = \
            user_with_metadata
        metadata = get_sheet(user_with_metadata, IMetadata)
        appstruct = metadata.get()
        appstruct['creation_date'] = datetime(
            year=2010, month=1, day=1, tzinfo=timezone.utc)
        metadata.set(appstruct, omit_readonly=False)
        self.call_fut(context, _request)
        assert 'Unknown or expired activation path' == _request.errors[0][
            'description']


class TestActivateAccountView:

    @fixture
    def request(self, cornice_request, registry):
        cornice_request.registry=registry
        cornice_request.validated['user'] = testing.DummyResource()
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import ActivateAccountView
        return ActivateAccountView(context, request)

    def test_post(self, request, context, mock_authpolicy):
        mock_authpolicy.remember.return_value = {'X-User-Path': '/user',
                                                 'X-User-Token': 'token'}
        inst = self.make_one(context, request)
        assert inst.post() == {'status': 'success',
                               'user_path': '/user',
                               'user_token': 'token'}

    def test_options(self, request, context):
        inst = self.make_one(context, request)
        assert inst.options() == {}


class TestReportAbuseView:

    @fixture
    def request(self, cornice_request, registry):
        from adhocracy_core.messaging import Messenger
        registry.messenger = Mock(spec=Messenger)
        cornice_request.registry = registry
        cornice_request.validated['url'] = 'http://localhost/blablah'
        cornice_request.validated['remark'] = 'Too much blah!'
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import ReportAbuseView
        return ReportAbuseView(context, request)

    def test_post(self, request, context):
        inst = self.make_one(context, request)
        assert inst.post() == ''
        assert request.registry.messenger.send_abuse_complaint.called

    def test_options(self, request, context):
        inst = self.make_one(context, request)
        assert inst.options() == {}


class TestMessageUserView:

    @fixture
    def request(self, cornice_request, registry):
        from adhocracy_core.messaging import Messenger
        registry.messenger = Mock(spec=Messenger)
        cornice_request.registry = registry
        cornice_request.validated['recipient'] = testing.DummyResource()
        cornice_request.validated['title'] = 'Important Adhocracy notice'
        cornice_request.validated['text'] = 'Surprisingly enough, all is well.'
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import MessageUserView
        return MessageUserView(context, request)

    def test_post(self, request, context):
        inst = self.make_one(context, request)
        assert inst.post() == ''
        assert request.registry.messenger.send_message_to_user.called

    def test_options_with_permission(self, request, context):
        inst = self.make_one(context, request)
        result = inst.options()
        assert 'POST' in result
        assert result['POST']['request_body'] == {'recipient': None,
                                                  'text': '',
                                                  'title': ''}
        assert result['POST']['response_body'] == ''

    def test_options_without_permission(self, request, context):
        from pyramid.request import Request
        request.has_permission = Mock(spec=Request.has_permission,
                                      return_value=False)
        inst = self.make_one(context, request)
        assert inst.options() == {}


class TestAssetsServiceRESTView:

    @fixture
    def request(self, cornice_request, mock_content_registry):
        cornice_request.registry.content = mock_content_registry
        return cornice_request

    def make_one(self, context, request):
        from adhocracy_core.rest.views import AssetsServiceRESTView
        return AssetsServiceRESTView(context, request)

    def test_post_valid(self, request, context):
        request.root = context
        child = testing.DummyResource(__provides__=IResourceX)
        child.__parent__ = context
        child.__name__ = 'child'
        request.registry.content.create.return_value = child
        request.validated = {'content_type': IResourceX, 'data': {}}
        inst = self.make_one(context, request)
        response = inst.post()
        wanted = {'path': request.application_url + '/child/',
                  'content_type': IResourceX.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert wanted == response


class TestAssetRESTView:

    @fixture
    def request_(self, cornice_request, mock_content_registry):
        cornice_request.registry.content = mock_content_registry
        return cornice_request

    def make_one(self, context, request_):
        from adhocracy_core.rest.views import AssetRESTView
        return AssetRESTView(context, request_)

    def test_put_valid_no_sheets(self, monkeypatch, request_, context,
                                 mock_sheet):
        from adhocracy_core.rest import views
        mock_validate = Mock(spec=views.validate_and_complete_asset)
        monkeypatch.setattr(views, 'validate_and_complete_asset',
                            mock_validate)
        request_.registry.content.get_sheets_edit.return_value = [mock_sheet]
        request_.validated = {"content_type": "X", "data": {}}
        inst = self.make_one(context, request_)
        response = inst.put()
        wanted = {'path': request_.application_url + '/',
                  'content_type': IResource.__identifier__,
                  'updated_resources': {'changed_descendants': [],
                                        'created': [],
                                        'modified': [],
                                        'removed': []}}
        assert wanted == response
        assert mock_validate.called


class TestAssetDownloadRESTView:

    @fixture
    def request_(self, cornice_request, mock_content_registry):
        cornice_request.registry.content = mock_content_registry
        return cornice_request

    def make_one(self, context, request_):
        from adhocracy_core.rest.views import AssetDownloadRESTView
        return AssetDownloadRESTView(context, request_)

    def test_get_ensure_caching_headers_called(self, monkeypatch, request_,
                                               context):
        from adhocracy_core.rest import views
        mock_file = Mock()
        mock_retrieve = Mock(return_value=mock_file)
        mock_response = Mock()
        mock_file.get_response = Mock(return_value=mock_response)
        monkeypatch.setattr(views, 'retrieve_asset_file', mock_retrieve)
        inst = self.make_one(context, request_)
        inst.ensure_caching_headers = Mock()
        inst.get()
        assert inst.ensure_caching_headers.called

    def test_ensure_caching_headers(self, context, request_):
        inst = self.make_one(context, request_)
        request_.response = testing.DummyResource(cache_control='cache_control',
                                                  etag='etag',
                                                  last_modified='last_modified')
        response = testing.DummyResource()
        inst.ensure_caching_headers(response)
        assert response.last_modified == 'last_modified'
        assert response.etag == 'etag'
        assert response.cache_control == 'cache_control'

    def test_get_valid_with_sheets(self, monkeypatch, request_, context):
        from adhocracy_core.rest import views
        mock_file = Mock()
        mock_retrieve = Mock(spec=views.retrieve_asset_file,
                             return_value=mock_file)
        mock_response = Mock()
        mock_file.get_response = Mock(return_value=mock_response)
        monkeypatch.setattr(views, 'retrieve_asset_file', mock_retrieve)
        inst = self.make_one(context, request_)
        assert inst.get() == mock_response


class TestShowRequestBody:

    def test_normal(self, cornice_request):
        from adhocracy_core.rest.views import _show_request_body
        cornice_request.body = "hello"
        assert _show_request_body(cornice_request) == "hello"

    def test_long_multipart_formdata_body_is_abbreviated(self,
                                                         cornice_request):
        from adhocracy_core.rest.views import _show_request_body
        cornice_request.content_type = 'multipart/form-data'
        cornice_request.body = "hello" * 30
        result = _show_request_body(cornice_request)
        assert len(result) < len(cornice_request.body)
        assert result.endswith('...')

    def test_password_is_hidden(self, cornice_request):
        import json
        from adhocracy_core.rest.views import _show_request_body
        cornice_request.body = json.dumps({'name': 'foo', 'password': 'bar'})
        result = _show_request_body(cornice_request)
        assert '"<hidden>"' in result
        assert 'bar' not in result

    def test_other_content_type(self, cornice_request):
        """Just the request body is returned in case of other content types."""
        from adhocracy_core.rest.views import _show_request_body
        cornice_request.content_type = 'text/plain'
        cornice_request.body = 'password: foofoo'
        result = _show_request_body(cornice_request)
        assert result == cornice_request.body


class TestCreatePasswordResetView:

    @fixture
    def resets(self, context, service):
        context['resets'] = service

    @fixture
    def request_(self, cornice_request, registry_with_content):
        cornice_request.registry = registry_with_content
        cornice_request.validated['user'] = testing.DummyResource()
        return cornice_request

    @fixture
    def mock_remember(self, monkeypatch):
        from pyramid.security import remember
        from . import views
        mock_remember = Mock(spec=remember)
        monkeypatch.setattr(views, 'remember', mock_remember)
        return mock_remember

    def make_one(self, context, request):
        from adhocracy_core.rest.views import CreatePasswordResetView
        return CreatePasswordResetView(context, request)

    def test_create(self, context, request_):
        from .schemas import POSTCreatePasswordResetRequestSchema
        inst = self.make_one(context, request_)
        assert inst.validation_POST == (POSTCreatePasswordResetRequestSchema,
                                        [])

    def test_post(self, request_, context, registry, resets):
        from adhocracy_core.resources.principal import IPasswordReset
        inst = self.make_one(context, request_)
        reset = testing.DummyResource(__name__='reset')
        registry.content.create.return_value = reset
        result = inst.post()
        registry.content.create.assert_called_with(
            IPasswordReset.__identifier__,
            resets,
            creator=request_.validated['user'])
        assert result == {'status': 'success'}

    def test_options(self, request_, context):
        inst = self.make_one(context, request_)
        assert inst.options() == {'POST': {}}


class TestPasswordResetView:

    @fixture
    def request_(self, cornice_request, registry_with_content):
        cornice_request.registry = registry_with_content
        return cornice_request

    @fixture
    def mock_remember(self, monkeypatch):
        from pyramid.security import remember
        from . import views
        mock_remember = Mock(spec=remember)
        monkeypatch.setattr(views, 'remember', mock_remember)
        return mock_remember

    def make_one(self, context, request):
        from adhocracy_core.rest.views import PasswordResetView
        return PasswordResetView(context, request)

    def test_create(self, context, request_):
        from .schemas import POSTPasswordResetRequestSchema
        inst = self.make_one(context, request_)
        assert inst.validation_POST == (POSTPasswordResetRequestSchema,
                                        [])

    def test_post(self, request_, context, mock_remember):
        from adhocracy_core.resources.principal import PasswordReset
        mock_reset = Mock(spec=PasswordReset)
        request_.validated['user'] = testing.DummyResource()
        request_.validated['path'] = mock_reset
        request_.validated['password'] = 'password'
        mock_remember.return_value = {'X-User-Path': '/',
                                      'X-User-Token': 'token'}
        inst = self.make_one(context, request_)
        result = inst.post()
        mock_reset.reset_password.assert_called()
        mock_remember.assert_called_with(request_, '/')
        mock_reset.reset_password.assert_called_with('password')
        assert result == {'status': 'success',
                          'user_path': '/',
                          'user_token': 'token'}

    def test_options(self, request_, context):
        inst = self.make_one(context, request_)
        assert inst.options() == {'POST': {}}


@fixture()
def integration(config):
    config.include('cornice')
    config.include('adhocracy_core.rest.views')


@mark.usefixtures('integration')
class TestIntegrationIncludeme:

    def test_includeme(self):
        """Check that includeme runs without errors."""
        assert True

