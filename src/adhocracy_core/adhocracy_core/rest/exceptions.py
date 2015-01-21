"""Rest API exceptions."""
import logging

from cornice.util import _JSONError
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pyramid.traversal import resource_path
import colander

from adhocracy_core.exceptions import AutoUpdateNoForkAllowedError
from adhocracy_core.utils import exception_to_str
from adhocracy_core.utils import log_compatible_datetime
from adhocracy_core.utils import named_object


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
    context=Exception,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_500_exception(error, request):
    """Return 500 JSON error."""
    error_dict = internal_exception_to_dict(error)
    logger.exception('internal')
    return _JSONError([error_dict], 500)


def internal_exception_to_dict(error: Exception) -> dict:
    """Convert an internal exception into a Colander-style dictionary."""
    description = '{}; time: {}'.format(exception_to_str(error),
                                        log_compatible_datetime())
    return _build_error_dict('internal', '', description)


def includeme(config):  # pragma: no cover
    """Include pyramid configuration."""
    config.scan('.exceptions')
