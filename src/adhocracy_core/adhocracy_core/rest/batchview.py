"""POST batch requests processing."""
from json import dumps
from logging import getLogger
from pyramid.httpexceptions import HTTPException
from pyramid.httpexceptions import HTTPClientError

from adhocracy_core.interfaces import API_ROUTE_NAME
from adhocracy_core.rest.exceptions import handle_error_x0x_exception
from adhocracy_core.rest.exceptions import handle_error_40x_exception
from adhocracy_core.rest.exceptions import handle_error_500_exception
from adhocracy_core.rest.exceptions import JSONHTTPClientError
from adhocracy_core.rest.exceptions import get_json_body
from adhocracy_core.authentication import AnonymizeHeader
from adhocracy_core.authentication import UserPasswordHeader
from pyramid.request import Request
from pyramid.interfaces import IRequest
from pyramid.view import view_defaults

from adhocracy_core.resources.root import IRootPool
from adhocracy_core.rest import api_view
from adhocracy_core.rest.schemas import POSTBatchRequestSchema
from adhocracy_core.rest.schemas import UpdatedResourcesSchema
from adhocracy_core.rest.views import _build_updated_resources_dict
from adhocracy_core.utils import set_batchmode
from adhocracy_core.utils import create_schema


logger = getLogger(__name__)


class BatchItemResponse:
    """Wrap the response to a nested request in a batch request.

    Attributes:

    :code: the status code (int)
    :title: the status title (str)
    :body: the response body as a JSOn object (dict)
    """

    def __init__(self, code: int, title: str, body: dict={}):
        """Initialize self."""
        self.code = code
        self.body = body
        self.title = title

    def was_successful(self):
        """Return true if batch was successful."""
        return self.code == 200

    def to_dict(self):
        """Convert to dict."""
        return {'code': self.code, 'body': self.body}


@view_defaults(
    context=IRootPool,
    name='batch',
)
class BatchView:
    """Process batch requests."""

    def __init__(self, context: IRootPool, request: IRequest):
        self.context = context
        self.request = request
        self.registry = request.registry

    @api_view(
        request_method='POST',
        schema=POSTBatchRequestSchema,
        accept='application/json',
    )
    def post(self) -> dict:
        """Create new resource and get response data."""
        response_list = []
        path_map = {}
        set_batchmode(self.request)
        for pos, item in enumerate(self.request.validated):
            item_response = self._process_nested_request(item, path_map)
            response_list.append(item_response)
            if not item_response.was_successful():
                error = JSONHTTPClientError([],
                                            code=item_response.code,
                                            title=item_response.title,
                                            request=self.request)
                # TODO: the error response lists updated resources
                json_body = error.json_body
                response_list_json = self._response_list_to_json(response_list)
                json_body.update(response_list_json)
                error.json_body = json_body
                msg = 'Failing batch request item position {0} request {1} {2}'
                logger.warn(msg.format(pos,
                                       item['method'],
                                       item['path']))
                raise error
        response = self._response_list_to_json(response_list)
        return response

    @api_view(request_method='OPTIONS')
    def options(self) -> dict:
        """Return options for batch view.

        This currently only exist in order to satisfy the preflight request,
        which browsers do in CORS situations before doing the actual POST.

        """
        return {}

    def _process_nested_request(self, nested_request: dict,
                                path_map: dict) -> BatchItemResponse:
        result_path = nested_request['result_path']
        result_first_version_path = nested_request['result_first_version_path']
        nested_request['path'] = self._resolve_preliminary_paths(
            nested_request['path'], path_map)
        nested_request['body'] = self._resolve_preliminary_paths(
            nested_request['body'], path_map)
        subrequest = self._make_subrequest(nested_request)
        item_response = self._invoke_subrequest_and_handle_errors(subrequest)
        self._extend_path_map(path_map, result_path, result_first_version_path,
                              item_response)
        return item_response

    def _response_list_to_json(self, response_list: list) -> list:
        """
        Convert the list of batch responses into a JSON dict.

        The dict has two fields:

        * responses: the list of batch responses, but without their
          "updated_resources" child element
        * updated_resources: the listing of resources affected by the
          transaction
        """
        responses = []
        for response in response_list:
            if 'updated_resources' in response.body:
                del response.body['updated_resources']
            responses.append(response.to_dict())
        updated_resources = _build_updated_resources_dict(self.registry)
        schema = create_schema(UpdatedResourcesSchema,
                               self.context,
                               self.request)
        return {'responses': responses,
                'updated_resources': schema.serialize(updated_resources)}

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

    def _make_subrequest(self, nested_request: dict) -> IRequest:
        path = nested_request['path']
        method = nested_request['method']
        json_body = nested_request['body']
        keywords_args = {'method': method,
                         'base_url': self.request.host_url}

        if json_body:
            keywords_args['body'] = dumps(json_body).encode()
        if method not in ['GET', 'OPTIONS', 'HEAD']:
            keywords_args['content_type'] = 'application/json'

        request = Request.blank(path, **keywords_args)
        set_batchmode(request)
        self.copy_attr_if_exists('root', request)
        self.copy_attr_if_exists('__cached_principals__', request)
        self.copy_attr_if_exists('__cached_userid__', request)
        self.copy_header_if_exists('X-User-Path', request)
        self.copy_header_if_exists('X-User-Token', request)
        self.copy_header_if_exists(AnonymizeHeader, request)
        self.copy_header_if_exists(UserPasswordHeader, request)

        # properly setup subrequest in case script_name env is set,
        # see https://github.com/Pylons/pyramid/issues/1434
        request.script_name = self.request.script_name

        # if a script_name (a prefix in front of backend paths, e.g. /api) is
        # set, subrequest paths also need to start with it.
        if not request.path_info.startswith(request.script_name):
            raise Exception('Batch subrequest path (%s) does not start with '
                            'script name (%s)' % (request.path_info,
                                                  request.script_name))

        request.path_info = request.path_info[len(self.request.script_name):]

        return request

    def _invoke_subrequest_and_handle_errors(
            self, subrequest: IRequest) -> BatchItemResponse:
        try:
            subresponse = self.request.invoke_subrequest(subrequest)
        except Exception as err:
            error_view = self._get_error_view(err)
            subresponse = error_view(err, subrequest)
        body = get_json_body(subresponse)
        return BatchItemResponse(subresponse.status_code,
                                 subresponse.status,
                                 body)

    def _get_error_view(self, error: Exception) -> callable:
        """Return view callable to handle exception.

        The error handler in :mod:`adhocracy_core.rest.exceptions` are only
        called at end of the request, but not for sub requests. To make
        sure batch requests show the same error messages as normal requests
        we try to find the right error view manually here.
        """
        if isinstance(error, HTTPException):
            error_view = handle_error_x0x_exception
        else:
            error_view = handle_error_500_exception
        if isinstance(error, HTTPClientError):
            error_view = handle_error_40x_exception
        instrospector = self.request.registry.introspector
        for view in instrospector.get_category('views'):
            context = view['introspectable']['context']
            route_name = view['introspectable']['route_name']
            if context == error.__class__ and route_name == API_ROUTE_NAME:
                error_view = view['introspectable']['callable']
                break
        return error_view

    def _extend_path_map(self, path_map: dict, result_path: str,
                         result_first_version_path: str,
                         item_response: BatchItemResponse):
        if not (result_path and item_response.was_successful()):
            return
        path = item_response.body.get('path', '')
        first_version_path = item_response.body.get('first_version_path', '')
        if path:
            path_map[result_path] = path
        if first_version_path:
            path_map[result_first_version_path] = first_version_path

    def copy_header_if_exists(self, header: str, request: IRequest):
        """Copy header if exists."""
        value = self.request.headers.get(header, None)
        if value is not None:
            request.headers[header] = value

    def copy_attr_if_exists(self, attributename: str, request: IRequest):
        """Copy attr if exists."""
        value = getattr(self.request, attributename, None)
        if value is not None:
            setattr(request, attributename, value)


def includeme(config):  # pragma: no cover
    """Register batch view."""
    config.scan('.batchview')
