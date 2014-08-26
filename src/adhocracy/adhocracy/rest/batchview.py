"""Rest API view for batch API."""
from json import dumps
from json import loads
from logging import getLogger

from cornice.util import _JSONError
from pyramid.httpexceptions import HTTPException
from pyramid.request import Request
from pyramid.view import view_config
from pyramid.view import view_defaults

from adhocracy.resources.root import IRootPool
from adhocracy.rest.exceptions import internal_exception_to_dict
from adhocracy.rest.schemas import POSTBatchRequestSchema
from adhocracy.rest.views import RESTView

logger = getLogger(__name__)


class BatchItemResponse:

    """Wrap the response to a nested request in a batch request.

    Attributes:

    :code: the status code (int)
    :body: the response body as a JSOn object (dict)
    """

    def __init__(self, code: int, body: dict={}):
        self.code = code
        self.body = body

    def was_successful(self):
        return self.code == 200

    def to_dict(self):
        return {'code': self.code, 'body': self.body}


@view_defaults(
    renderer='simplejson',
    context=IRootPool,
    http_cache=0,
)
class BatchView(RESTView):

    """Process batch requests."""

    validation_POST = (POSTBatchRequestSchema, [])

    @view_config(name='batch',
                 request_method='POST',
                 content_type='application/json')
    def post(self) -> dict:
        """Create new resource and get response data."""
        response_list = []
        path_map = {}
        for item in self.request.validated:
            item_response = self._process_nested_request(item, path_map)
            response_list.append(item_response)
            if not item_response.was_successful():
                err = _JSONError([], status=item_response.code)
                err.text = dumps(self._response_list_to_json(response_list))
                raise err
        return self._response_list_to_json(response_list)

    def _process_nested_request(self, nested_request: dict,
                                path_map: dict) -> BatchItemResponse:
        result_path = nested_request['result_path']
        nested_request['path'] = self._resolve_preliminary_paths(
            nested_request['path'], path_map)
        nested_request['body'] = self._resolve_preliminary_paths(
            nested_request['body'], path_map)
        subrequest = self._make_subrequest(nested_request)
        item_response = self._invoke_subrequest_and_handle_errors(subrequest)
        self._extend_path_map(path_map, result_path, item_response)
        return item_response

    def _response_list_to_json(self, response_list: list) -> list:
        return [response.to_dict() for response in response_list]

    def _resolve_preliminary_paths(self, json_value: object,
                                   path_map: dict) -> object:
        """Create a copy of `json_value` with preliminary paths resolved.

        This method accepts arbitrary JSON values and calls itself
        recursively, as needed. In trivial cases (no change necessary),
        the original `json_value` may be returned instead of a copy.
        """
        if not (path_map and json_value):
            return json_value
        if isinstance(json_value, str):
            result = path_map.get(json_value, json_value)
        elif isinstance(json_value, dict):
            result = {}
            for key, value in json_value.items():
                result[key] = self._resolve_preliminary_paths(value, path_map)
        elif isinstance(json_value, list):
            result = []
            for value in json_value:
                result.append(self._resolve_preliminary_paths(value, path_map))
        else:
            result = json_value
        return result

    def _make_subrequest(self, nested_request: dict) -> Request:
        path = nested_request['path']
        method = nested_request['method']
        json_body = nested_request['body']
        keywords_args = {'method': method}

        if json_body:
            keywords_args['body'] = dumps(json_body).encode()
        if method != 'GET':
            keywords_args['content_type'] = 'application/json'

        request = Request.blank(path, **keywords_args)
        request.root = self.request.root
        return request

    def _invoke_subrequest_and_handle_errors(
            self, subrequest: Request) -> BatchItemResponse:
        try:
            subresponse = self.request.invoke_subrequest(subrequest)
            code = subresponse.status_code
            body = subresponse.json
        except HTTPException as err:
            code = err.status_code
            body = self._try_to_decode_json(err.body)
        except Exception as err:
            code = 500
            error_dict = internal_exception_to_dict(err)
            body = {'status': 'error', 'errors': [error_dict]}
            logger.exception('Unexpected exception processing nested request')
        return BatchItemResponse(code, body)

    def _extend_path_map(self, path_map: dict, result_path: str,
                         item_response: BatchItemResponse):
        if not (result_path and item_response.was_successful()):
            return
        path = item_response.body.get('path', '')
        first_version_path = item_response.body.get('first_version_path', '')
        if path:
            path_map['@' + result_path] = path
        if first_version_path:
            path_map['@@' + result_path] = first_version_path

    def _try_to_decode_json(self, body: bytes) -> dict:
        """Try to decode `body` as a JSON object.

        If that fails, we just wrap the textual content of the body in an
        `{"error": ...}` dict. If body is empty, we just return an empty dict.
        """
        if not body:
            return {}
        text = body.decode(errors='replace')
        try:
            return loads(text)
        except ValueError:
            return {'error': text}


def includeme(config):  # pragma: no cover
    """Register batch view."""
    config.scan('.batchview')
