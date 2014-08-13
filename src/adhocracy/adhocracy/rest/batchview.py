"""Rest API view for batch API."""
from json import dumps
from logging import getLogger

from pyramid.request import Request
from pyramid.view import view_config
from pyramid.view import view_defaults

from adhocracy.resources.root import IRootPool
from adhocracy.rest.schemas import POSTBatchRequestSchema
from adhocracy.rest.views import RESTView

logger = getLogger(__name__)


class BatchItemResponse():

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
)
class BatchView(RESTView):

    """Process batch requests."""

    validation_POST = (POSTBatchRequestSchema, [])

    @view_config(name='batch',
                 request_method='POST',
                 content_type='application/json')
    def post(self) -> dict:
        """Create new resource and get response data."""
        items = self.request.validated['items']
        response_list = []
        path_map = {}
        for item in items:
            item_response = self._process_nested_request(item, path_map)
            response_list.append(item_response)
            if not item_response.was_successful():
                break
        return [response.to_dict() for response in response_list]

    def _process_nested_request(self, nested_request: dict,
                                path_map: dict) -> BatchItemResponse:
        result_path = nested_request['result_path']
        # TODO resolve preliminary names in body
        subrequest = self._make_subrequest(nested_request)
        subresponse = self.request.invoke_subrequest(subrequest)
        logger.debug(result_path)  # TODO To make check_code happy
        # TODO add result_path mapping, if defined and successful
        # (also @@first version path):_extend_path_map(result_path, ...)
        return BatchItemResponse(subresponse.status_code, subresponse.json)

    def _make_subrequest(self, nested_request: dict):
        path = nested_request['path']
        method = nested_request['method']
        json_body = nested_request['body']
        if json_body:
            body = dumps(json_body).encode(self.request.charset)
        else:
            body = None
        return Request(environ=self.request.environ,
                       charset=self.request.charset,
                       content_type='application/json',
                       method=method, path_info=path, body=body)


def includeme(config):  # pragma: no cover
    """Register batch view."""
    config.scan('.batchview')
