"""HTTP Exception (500, 310, 404,..) processing."""
import json
import logging
import colander
from collections import namedtuple

from cornice.util import _JSONError
from pyramid.exceptions import URLDecodeError
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pyramid.traversal import resource_path
from pyramid.httpexceptions import HTTPGone
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPException
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


@view_config(
    context=HTTPException,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_xox_exception(error, request):
    """Return JSON error for generic HTTPErrors.

     If `error` is :class:`cornice.util._JSONError` it is
    return without modifications.
    """
    if isinstance(error, _JSONError):
        return error
    error_dict = error_entry('url', request.method, str(error))._asdict()
    json_error = _JSONError([error_dict], error.status_code)
    return json_error


@view_config(
    context=colander.Invalid,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_400_colander_invalid(error, request):
    """Return 400 JSON error."""
    errors = []
    for path, description in error.asdict().items():
        error_dict = error_entry('body', path, description)._asdict()
        errors.append(error_dict)
    return _JSONError(errors, 400)


@view_config(
    context=HTTPBadRequest,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_400_bad_request(error, request):
    """Return 400 JSON error with filtered error messages."""
    errors = getattr(request, 'errors', [])  # ease testing
    body = _get_filtered_request_body(request)
    log_msg = 'Found {0} validation errors in request body: {1}'
    logger.warning(log_msg.format(len(errors), body))
    for error_data in errors:
        logger.warning(' {0}'.format(error_data))
    return _JSONError(errors, 400)


def _get_filtered_request_body(request) -> str:
    """
    Filter secret or to long parts of the request body.

    In case of multipart/form-data requests (file upload),
    only the 120 first characters of the body are shown.

    In case of JSON request, the contents of the password field will be hidden.
    Only the 5000 first characters are shown.
    """
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
    http_cache=0,
)
def handle_error_400_auto_update_no_fork_allowed(error, request):
    """Return 400 JSON error for the internal "No Fork allowed" error.

    Assuming there was a post request with wrong values for 'root_versions'.
    """
    msg = 'No fork allowed'
    args = (resource_path(error.resource),
            error.event.isheet.__identifier__,
            error.event.isheet_field,
            resource_path(error.event.old_version),
            resource_path(error.event.new_version))
    description = ' - The auto update tried to create a fork for: {0} caused '\
                  'by isheet: {1} field: {2} with old_reference: {3} and new '\
                  'reference: {4}. Try another root_version.'.format(*args)
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
    error_dict = error_entry('url', '', str(error))._asdict()
    return _JSONError([error_dict], 400)


@view_config(
    context=Exception,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_500_exception(error, request):
    """Return 500 JSON error."""
    error_dict = internal_exception_to_dict(error)
    logger.exception('internal')
    return _JSONError([error_dict], 500)


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
    error.text = json.dumps(cstruct)
    return error


def internal_exception_to_dict(error: Exception) -> dict:
    """Convert an internal exception into a Colander-style dictionary."""
    description = '{}; time: {}'.format(exception_to_str(error),
                                        log_compatible_datetime())
    return error_entry('internal', '', description)._asdict()


@view_config(context=HTTPForbidden,
             permission=NO_PERMISSION_REQUIRED,
             )
def handle_error_403_exception(error, request):
    """Add json body with explanation to 403 errors.

    This overrides the same error handler in :mod:`cornice`.
    """
    error_dict = error_entry('url', request.method, str(error))._asdict()
    return _JSONError([error_dict], 403)


@view_config(context=HTTPNotFound,
             permission=NO_PERMISSION_REQUIRED,
             )
def handle_error_404_exception(error, request):
    """Add json body with explanation to 404 errors.

    This overrides the same error handler in :mod:`cornice`.
    """
    error_dict = error_entry('url', request.method, str(error))._asdict()
    return _JSONError([error_dict], 404)


def includeme(config):  # pragma: no cover
    """Include pyramid configuration."""
    config.scan('.exceptions')
