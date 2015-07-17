"""HTTP Exception (500, 310, 404,..) processing."""
import json
import logging
import colander
from collections import namedtuple

from pyramid.exceptions import URLDecodeError
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pyramid.traversal import resource_path
from pyramid.httpexceptions import HTTPGone
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPException
from pyramid.httpexceptions import HTTPClientError
from pyramid.request import Request

from adhocracy_core.exceptions import AutoUpdateNoForkAllowedError
from adhocracy_core.utils import exception_to_str
from adhocracy_core.utils import log_compatible_datetime
from adhocracy_core.utils import named_object
from adhocracy_core.sheets.metadata import view_blocked_by_metadata
from adhocracy_core.sheets.principal import IPasswordAuthentication
from adhocracy_core.rest.schemas import BlockExplanationResponseSchema


logger = logging.getLogger(__name__)


error_entry = namedtuple('ErrorEntry', ['location', 'name', 'description'])


class JSONHTTPClientError(HTTPClientError):

    """HTTPException with json body to describe the exception.

    :param:`errors`: error entries to generate the error description.
    :param:`request`: Request causing the error to log debug information.
    :param:`code`: http status code
    :param:`title`: http status title

    The body contains a dictionary with the following data structure:

    * `status`: 'error'

    * `errors`: [error_entry]
    """

    def __init__(self, error_entries: [error_entry],
                 request: Request=None,
                 code: int=400,
                 title: str='Bad Request'):
        self.code = code
        self.title = title
        super().__init__()
        self.content_type = 'application/json'
        self.json_body = {'status': 'error',
                          'errors': [e._asdict() for e in error_entries]}
        body = _get_filtered_request_body(request)
        logger.warn('Found errors in request with body: {0}\n'.format(body))
        for error in error_entries:
            logger.warning('Validation Error: {0}\n'.format(error._asdict()))


@view_config(
    context=Exception,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_500_exception(error, request):
    """Return 500 JSON error."""
    logger.exception('internal')
    description = '{}; time: {}'.format(exception_to_str(error),
                                        log_compatible_datetime())
    error_entries = [error_entry('internal', '', description)]
    return JSONHTTPClientError(error_entries,
                               request=request,
                               code=500,
                               title='Internal Server Error')


@view_config(
    context=HTTPException,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_x0x_exception(error, request):
    """Return HTTPError."""
    return error


@view_config(
    context=HTTPClientError,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_40x_exception(error, request):
    """Return JSON error for generic HTTPClientErrors.

     If `error` is :class:`JSONHTTPClientError` it is
    return without modifications.
    """
    if isinstance(error, JSONHTTPClientError):
        return error
    error_entries = [error_entry('url', request.method, str(error))]
    json_error = JSONHTTPClientError(error_entries,
                                     request=request,
                                     code=error.code,
                                     title=error.title)
    return json_error


@view_config(
    context=colander.Invalid,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_400_colander_invalid(invalid, request):
    """Return JSON error for colander.Invalid errors."""
    errors = [error_entry('body', n, d) for n, d in invalid.asdict().items()]
    return JSONHTTPClientError(errors, request=request)


@view_config(
    context=HTTPBadRequest,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_400_bad_request(error, request):
    """Return 400 JSON error with filtered error messages."""
    error_entries = getattr(request, 'errors', [])  # ease testing
    return JSONHTTPClientError(error_entries, request=request)


def _get_filtered_request_body(request) -> str:
    """
    Filter secret or to long parts of the request body.

    In case of multipart/form-data requests (file upload),
    only the 120 first characters of the body are shown.

    In case of JSON request, the contents of the password field will be hidden.
    Only the 5000 first characters are shown.
    """
    if request is None:
        return ''
    filtered_body = request.body
    if request.content_type == 'multipart/form-data':
        filtered_body = _truncate(filtered_body, 120)
    else:
        json_body = _get_json_body_dict(request)
        if 'password' in json_body:
            json_body['password'] = '<hidden>'
        password_sheet = IPasswordAuthentication.__identifier__
        if password_sheet in json_body.get('data', {}):
            json_body['data'][password_sheet]['password'] = '<hidden>'
        filtered_body = json.dumps(json_body)
        filtered_body = _truncate(filtered_body, 5000)
    return filtered_body


def _truncate(text: str, max_length: int) -> str:
        if len(text) > max_length:
            text = '{}...'.format(text[:max_length])
        return text


def _get_json_body_dict(request: Request) -> dict:
    body_json = {}
    try:
        body_json = request.json_body
    except (ValueError, TypeError):
        pass
    if isinstance(body_json, dict):
        return body_json
    else:
        return {}


@view_config(
    context=AutoUpdateNoForkAllowedError,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_400_auto_update_no_fork_allowed(error, request):
    """Return 400 JSON error for the internal "No Fork allowed" error.

    Assuming there was a post request with wrong values for 'root_versions'.
    """
    msg = 'No fork allowed '
    args = (resource_path(error.resource),
            error.event.isheet.__identifier__,
            error.event.isheet_field,
            resource_path(error.event.old_version),
            resource_path(error.event.new_version))
    description = '- The auto update tried to create a fork for: {0} caused'\
                  ' by isheet: {1} field: {2} with old_reference: {3} and new'\
                  ' reference: {4}. Try another root_version.'.format(*args)
    dummy_node = named_object('root_versions')
    error_colander = colander.Invalid(dummy_node, msg + description)
    return handle_error_400_colander_invalid(error_colander, request)


@view_config(
    context=URLDecodeError,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_400_url_decode_error(error, request):
    """
    Handle error thrown by Pyramid if the request path is not valid UTF-8.

    E.g. "/fooba%E9r/".
    """
    error_entries = [error_entry('url', '', str(error))]
    return JSONHTTPClientError(error_entries)


@view_config(
    context=Exception,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_500_exception(error, request):
    """Return 500 JSON error."""
    logger.exception('internal')
    description = '{}; time: {}'.format(exception_to_str(error),
                                        log_compatible_datetime())
    error_entries = [error_entry('internal', '', description)]
    return JSONHTTPException(error_entries,
                             code=500,
                             title='Internal Server Error')


@view_config(context=HTTPGone,
             permission=NO_PERMISSION_REQUIRED,
             )
def handle_error_410_exception(error, request):
    """Add json body with explanation to 410 errors."""
    context = request.context
    registry = request.registry
    reason = error.detail or ''
    explanation = view_blocked_by_metadata(context, registry, reason)
    schema = BlockExplanationResponseSchema().bind(request=request,
                                                   context=context)
    cstruct = schema.serialize(explanation)
    error.content_type = 'application/json'
    if cstruct['modification_date'] is colander.null:
        cstruct['modification_date'] = ''
    error.json = cstruct
    return error


@view_config(context=HTTPForbidden,
             permission=NO_PERMISSION_REQUIRED,
             )
def handle_error_403_exception(error, request):
    """Add json body with explanation to 403 errors.

    This overrides the same error handler in :mod:`cornice`.
    """
    error_dict = error_entry('url', request.method, str(error))
    return JSONHTTPException([error_dict], code=403, title='Forbidden')


@view_config(context=HTTPNotFound,
             permission=NO_PERMISSION_REQUIRED,
             )
def handle_error_404_exception(error, request):
    """Add json body with explanation to 404 errors.

    This overrides the same error handler in :mod:`cornice`.
    """
    error_dict = error_entry('url', request.method, str(error))
    return JSONHTTPException([error_dict], code=404, title='Not Found')


def includeme(config):  # pragma: no cover
    """Include pyramid configuration."""
    config.scan('.exceptions')
