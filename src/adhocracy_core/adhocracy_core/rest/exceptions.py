"""HTTP Exception (500, 310, 404,..) processing."""
import json
import logging
import colander

from cornice.util import _JSONError
from pyramid.exceptions import URLDecodeError
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pyramid.traversal import resource_path
from pyramid.httpexceptions import HTTPGone
from pyramid.httpexceptions import HTTPBadRequest

from adhocracy_core.exceptions import AutoUpdateNoForkAllowedError
from adhocracy_core.utils import exception_to_str
from adhocracy_core.utils import log_compatible_datetime
from adhocracy_core.utils import named_object
from adhocracy_core.sheets.metadata import view_blocked_by_metadata
from adhocracy_core.sheets.principal import IPasswordAuthentication
from adhocracy_core.rest.schemas import BlockExplanationResponseSchema


logger = logging.getLogger(__name__)


@view_config(
    context=colander.Invalid,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_400_colander_invalid(error, request):
    """Return 400 JSON error."""
    errors = []
    for path, description in error.asdict().items():
        errors.append(_build_error_dict('body', path, description))
    return _JSONError(errors, 400)


def _build_error_dict(location, name, description):
    return {'location': location, 'name': name, 'description': description}


@view_config(
    context=HTTPBadRequest,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_400_bad_request(error, request):
    """Return 400 JSON error with filtered error messages."""
    errors = getattr(request, 'errors', [])  # ease testing
    body = _get_filtered_request_body(request)
    logger.warning('Found %i validation errors in request: <%s>',
                   len(errors), body)
    for error_data in errors:
        logger.warning('  %s', error_data)
    return _JSONError(errors, 400)


def _get_filtered_request_body(request) -> str:
    """
    Filter secret or to long parts of the request body.

    In case of multipart/form-data requests (file upload), only the 120
    first characters of the body are shown.

    In case of JSON requests with a "password" field,
    the contents of the password field will be hidden.
    """
    result = request.body
    if request.content_type == 'multipart/form-data' and len(result) > 120:
        result = '{}...'.format(result[:120])
    elif request.content_type == 'application/json':
        json_data = ''
        try:
            json_data = request.json_body
        except ValueError:
            pass  # Not even valid JSON, so we cannot filter anything
        if not isinstance(json_data, dict):
            pass
        possible_password_data = json_data
        if 'data' in json_data:
            possible_password_data = json_data['data'].get(
                IPasswordAuthentication.__identifier__, {})
        if 'password' in possible_password_data:
            loggable_data = possible_password_data.copy()
            loggable_data['password'] = '<hidden>'
            result = json.dumps(loggable_data)
    return result


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
    error_dict = _build_error_dict('url', '', str(error))
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
    return _build_error_dict('internal', '', description)


def includeme(config):  # pragma: no cover
    """Include pyramid configuration."""
    config.scan('.exceptions')
