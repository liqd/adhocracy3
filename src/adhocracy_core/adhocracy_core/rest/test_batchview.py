import json

from pyramid.request import Request
from pytest import fixture
from pytest import raises
from unittest.mock import Mock
from testfixtures import LogCapture


class DummySubresponse:

    def __init__(self, status_code=200, json: dict={}):
        self.status_code = status_code
        self.json = json


class TestBatchItemResponse:

    def make_one(self, code=200, body={}):
        from adhocracy_core.rest.batchview import BatchItemResponse
        return BatchItemResponse(code, body)

    def test_was_successful_true(self):
        inst = self.make_one()
        assert inst.was_successful() is True

    def test_was_successful_false(self):
        inst = self.make_one(404)
        assert inst.was_successful() is False

    def test_to_dict(self):
        inst = self.make_one()
        assert inst.to_dict() == {'code': 200, 'body': {}}


class TestBatchView:

    @fixture
    def mock_invoke_subrequest(self):
        mock = Mock()
        mock.return_value = DummySubresponse()
        return mock

    @fixture
    def request_(self, cornice_request, changelog, mock_invoke_subrequest):
        cornice_request.registry.changelog = changelog
        cornice_request.invoke_subrequest = mock_invoke_subrequest
        cornice_request.method = 'POST'
        return cornice_request

    @fixture
    def integration(self, config, changelog):
        config.include('adhocracy_core.rest')
        registry = config.registry
        registry.changelog = changelog
        return config

    def make_one(self, context, request_):
        from adhocracy_core.rest.batchview import BatchView
        return BatchView(context, request_)

    def _make_subrequest_cstruct(self, path: str='http://a.org/adhocracy/blah',
                                 result_path: str='@newpath',
                                 method: str='PUT',
                                 body: dict={},
                                 result_first_version_path: str='@newpath/v1',
                                 ) -> dict:
        return {'path': path,
                'result_path': result_path,
                'result_first_version_path': result_first_version_path,
                'method': method,
                'body': body}

    def _make_json_with_subrequest_cstructs(self, **kwargs) -> dict:
        cstruct = self._make_subrequest_cstruct(**kwargs)
        return json.dumps([cstruct])

    def test_post_empty(self, context, request_):
        from adhocracy_core.utils import is_batchmode
        inst = self.make_one(context, request_)
        assert inst.post() == {'responses': [],
                               'updated_resources': {'changed_descendants': [],
                                                     'created': [],
                                                     'modified': [],
                                                     'removed': []}}
        assert is_batchmode(request_)

    def test_post_successful_subrequest(self, context, request_, mock_invoke_subrequest):
        request_.body = self._make_json_with_subrequest_cstructs()
        inst = self.make_one(context, request_)
        paths = {'path': '/pool/item',
                 'first_version_path': '/pool/item/v1'}
        mock_invoke_subrequest.return_value = DummySubresponse(status_code=200,
                                                               json=paths,)
        response = inst.post()
        assert response == {'responses': [{'body': paths, 'code': 200}],
                            'updated_resources': {'changed_descendants': [],
                                                  'created': [],
                                                  'modified': [],
                                                  'removed': []}}

    def test_post_copy_special_request__attributes_headers_to_subrequest(
            self, context, request_, mock_invoke_subrequest):
        from pyramid.traversal import resource_path
        from adhocracy_core.utils import is_batchmode
        request_.body = self._make_json_with_subrequest_cstructs()
        request_.__cached_principals__ = [1]
        date = object()
        request_.headers['X-User-Path'] = 2
        request_.headers['X-User-Token'] = 3
        # Needed to stop the validator from complaining if these headers are
        # present
        request_.authenticated_userid = resource_path(context)
        request_.root = context
        request_.script_name = '/virtual'
        inst = self.make_one(context, request_)
        paths = {'path': '/pool/item',
                 'first_version_path': '/pool/item/v1'}
        mock_invoke_subrequest.return_value = DummySubresponse(status_code=200,
                                                               json=paths,)
        inst.post()
        subrequest  = mock_invoke_subrequest.call_args[0][0]
        assert is_batchmode(subrequest)
        assert subrequest.__cached_principals__ == [1]
        assert subrequest.headers.get('X-User-Path') == 2
        assert subrequest.headers.get('X-User-Token') == 3
        assert subrequest.script_name == '/virtual'
        assert subrequest.path_info == 'cy/blah'

    def test_post_successful_subrequest_with_updated_resources(
            self, context, request_, mock_invoke_subrequest):
        request_.body = self._make_json_with_subrequest_cstructs()
        inst = self.make_one(context, request_)
        response_body = {'path': '/pool/item',
                 'first_version_path': '/pool/item/v1',
                 'updated_resources': {'created': ['/pool/item/v1']}}
        mock_invoke_subrequest.return_value = DummySubresponse(
            status_code=200, json=response_body,)
        response = inst.post()
        assert response == {'responses': [{'body': {'path': '/pool/item',
                                                    'first_version_path':
                                                        '/pool/item/v1'},
                                           'code': 200}],
                            'updated_resources': {'changed_descendants': [],
                                                  'created': [],
                                                  'modified': [],
                                                  'removed': []}}

    def test_post_successful_subrequest_resolve_result_paths(self, context, request_, mock_invoke_subrequest):
        cstruct1 = self._make_subrequest_cstruct(result_first_version_path='@item/v1')
        cstruct2 = self._make_subrequest_cstruct(body={'ISheet': {'ref': '@item/v1'}})
        request_.body = json.dumps([cstruct1, cstruct2])
        inst = self.make_one(context, request_)
        paths = {'path': '/pool/item',
                 'first_version_path': '/pool/item/v1'}
        mock_invoke_subrequest.return_value = DummySubresponse(status_code=200,
                                                               json=paths)

        inst.post()

        subrequest2 = mock_invoke_subrequest.call_args[0][0]
        assert subrequest2.json ==  {'ISheet': {'ref': '/pool/item/v1'}}

    def test_post_failed_subrequest(self, context, request_, mock_invoke_subrequest):
        from .exceptions import JSONHTTPClientError
        request_.body = self._make_json_with_subrequest_cstructs()
        mock_invoke_subrequest.return_value = DummySubresponse(status_code=444)
        inst = self.make_one(context, request_)
        with raises(JSONHTTPClientError) as err:
            inst.post()
            assert err.status_code == 444
            assert err.text.startswith('[{')
            assert err.text.endswith('}]')

    def test_post_subrequest_with_http_client_exception(
            self, context, request_, mock_invoke_subrequest, integration):
        from pyramid.httpexceptions import HTTPUnauthorized
        from .exceptions import JSONHTTPClientError
        request_.registry = integration.registry
        request_.body = self._make_json_with_subrequest_cstructs()
        request_.validated = request_.json_body
        mock_invoke_subrequest.side_effect = HTTPUnauthorized()
        inst = self.make_one(context, request_)
        with raises(JSONHTTPClientError) as err:
            inst.post()
            assert err.status_code == 401

    def test_post_subrequest_with_http_400_exception(
            self, context, request_, mock_invoke_subrequest, integration):
        from pyramid.httpexceptions import HTTPBadRequest
        from .exceptions import JSONHTTPClientError
        request_.registry = integration.registry
        request_.body = self._make_json_with_subrequest_cstructs()
        mock_invoke_subrequest.side_effect = HTTPBadRequest()
        mock_invoke_subrequest.return_value.errors = [{'location': 'body'}]
        inst = self.make_one(context, request_)
        with raises(JSONHTTPClientError) as err:
            inst.post()
            assert err.status_code == 400

    def test_post_subrequest_with_http_redirect_exception(
            self, context, request_, mock_invoke_subrequest, integration):
        from pyramid.httpexceptions import HTTPRedirection
        from .exceptions import JSONHTTPClientError
        request_.registry = integration.registry
        request_.body = self._make_json_with_subrequest_cstructs()
        mock_invoke_subrequest.side_effect = HTTPRedirection()
        inst = self.make_one(context, request_)
        with raises(JSONHTTPClientError) as err:
            inst.post()
            assert err.status_code == 301

    def test_post_subrequest_with_non_http_exception(
            self, context, request_, mock_invoke_subrequest, integration):
        from .exceptions import JSONHTTPClientError
        request_.registry = integration.registry
        request_.body = self._make_json_with_subrequest_cstructs()
        mock_invoke_subrequest.side_effect = RuntimeError('Bad luck')
        inst = self.make_one(context, request_)
        with raises(JSONHTTPClientError) as err:
            with LogCapture() as log:
                inst.post()
            assert err.status_code == 500

    def _make_batch_response(self, code=200, path=None, first_version_path=None):
        from adhocracy_core.rest.batchview import BatchItemResponse
        body = {}
        if path is not None:
            body['path'] = path
        if first_version_path is not None:
            body['first_version_path'] = first_version_path
        return BatchItemResponse(code, body)

    def test_extend_path_map_just_path(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {}
        result_path = '@newpath'
        result_first_version_path = ''
        item_response = self._make_batch_response(path='http://a.org/adhocracy/new_item')
        inst._extend_path_map(path_map, result_path, result_first_version_path, item_response)
        assert path_map == {'@newpath': 'http://a.org/adhocracy/new_item'}

    def test_extend_path_map_just_path_and_missing_response_path(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {}
        result_path = '@newpath'
        result_first_version_path = ''
        item_response = self._make_batch_response()
        inst._extend_path_map(path_map, result_path, result_first_version_path, item_response)
        assert path_map == {}

    def test_extend_path_map_path_and_first_version_path(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {}
        result_path = '@newpath'
        result_first_version_path = '@newpath/v1'
        item_response = self._make_batch_response(
            path='/adhocracy/new_item',
            first_version_path='/adhocracy/new_item/v0')
        inst._extend_path_map(path_map, result_path, result_first_version_path, item_response)
        assert path_map == {'@newpath': '/adhocracy/new_item',
                            '@newpath/v1': '/adhocracy/new_item/v0'}

    def test_copy_header_if_exists_not_existing(self, context, request_):
        from copy import deepcopy
        inst = self.make_one(context, request_)
        subrequest = deepcopy(request_)
        inst.copy_header_if_exists('non_existing', subrequest)
        assert 'non_existing' not in subrequest.headers

    def test_copy_header_if_exists_existing(self, context, request_):
        from copy import deepcopy
        inst = self.make_one(context, request_)
        subrequest = deepcopy(request_)
        request_.headers['existing'] = 'Test'
        inst.copy_header_if_exists('existing', subrequest)
        assert 'existing' in subrequest.headers

    def test_copy_attr_if_exists_not_existing(self, context, request_):
        from copy import deepcopy
        inst = self.make_one(context, request_)
        subrequest = deepcopy(request_)
        inst.copy_attr_if_exists('non_existing', subrequest)
        assert not hasattr(subrequest, 'non_existing')

    def test_copy_attr_if_exists_not_exists(self, context, request_):
        from copy import deepcopy
        inst = self.make_one(context, request_)
        subrequest = deepcopy(request_)
        request_.existing = 'Buh'
        inst.copy_attr_if_exists('existing', subrequest)
        assert hasattr(subrequest, 'existing')

    def test_extend_path_map_no_result_path(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {}
        result_path = ''
        result_first_version_path = ''
        item_response = self._make_batch_response(path='/adhocracy/new_item')
        inst._extend_path_map(path_map, result_path, result_first_version_path, item_response)
        assert path_map == {}

    def test_extend_path_map_failed_response(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {}
        result_path = '@newpath'
        result_first_version_path = ''
        item_response = self._make_batch_response(code=444,
                                                  path='/adhocracy/new_item')
        inst._extend_path_map(path_map, result_path, result_first_version_path, item_response)
        assert path_map == {}

    def test_make_subrequest_post_with_non_empty_body(self, context, request_):
        inst = self.make_one(context, request_)
        body = {'content_type':
                    'adhocracy_core.resources.paragraph.IParagraph',
                'data': {'adhocracy_core.sheets.name.IName': {'name': 'par1'}}
               }
        subrequest_cstruct = self._make_subrequest_cstruct(method='POST', body=body)
        subrequest = inst._make_subrequest(subrequest_cstruct)
        assert isinstance(subrequest, Request)
        assert subrequest.method == 'POST'
        assert subrequest.content_type == 'application/json'
        assert subrequest.json == body

    def test_make_subrequest_get_with_empty_body(self, context, request_):
        inst = self.make_one(context, request_)
        subrequest_cstrut = self._make_subrequest_cstruct(method='GET')
        subrequest = inst._make_subrequest(subrequest_cstrut)
        assert subrequest.method == 'GET'
        assert subrequest.content_type != 'application/json'
        assert len(subrequest.body) == 0

    def test_resolve_preliminary_paths_str_with_replacement(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {'@newpath': '/adhocracy/new_item'}
        json_value = '@newpath'
        result = inst._resolve_preliminary_paths(json_value, path_map)
        assert result == '/adhocracy/new_item'

    def test_resolve_preliminary_paths_str_without_replacement(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {'@newpath': '/adhocracy/new_item'}
        json_value = 'nopath'
        result = inst._resolve_preliminary_paths(json_value, path_map)
        assert result == json_value

    def test_resolve_preliminary_paths_dict_with_replacement(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {'@newpath': '/adhocracy/new_item'}
        json_value = {'item1': 'foo', 'item2': '@newpath', 'item3': 'bar'}
        result = inst._resolve_preliminary_paths(json_value, path_map)
        assert result == {'item1': 'foo',
                          'item2': '/adhocracy/new_item',
                          'item3': 'bar'}

    def test_resolve_preliminary_paths_dict_without_replacement(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {'@newpath': '/adhocracy/new_item'}
        json_value = {'item1': 'foo', 'item2': 'nopath', 'item3': 'bar'}
        result = inst._resolve_preliminary_paths(json_value, path_map)
        assert result == json_value

    def test_resolve_preliminary_paths_list_with_replacement(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {'@newpath': '/adhocracy/new_item'}
        json_value = ['@newpath', 'foo', 'bar']
        result = inst._resolve_preliminary_paths(json_value, path_map)
        assert result == ['/adhocracy/new_item', 'foo', 'bar']

    def test_resolve_preliminary_paths_list_without_replacement(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {'@newpath': '/adhocracy/new_item'}
        json_value = ['nopath', 'foo', 'bar']
        result = inst._resolve_preliminary_paths(json_value, path_map)
        assert result == json_value

    def test_resolve_preliminary_paths_other_type(self, context, request_):
        inst = self.make_one(context, request_)
        path_map = {'@newpath': '/adhocracy/new_item'}
        json_value = 123.456
        result = inst._resolve_preliminary_paths(json_value, path_map)
        assert result == json_value

    def test_options_empty(self, context, request_):
        inst = self.make_one(context, request_)
        assert inst.options() == {}
