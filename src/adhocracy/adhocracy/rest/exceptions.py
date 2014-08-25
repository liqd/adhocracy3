"""Rest API exceptions."""
import logging

from cornice.util import _JSONError
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
import colander


logger = logging.getLogger(__name__)


@view_config(
    context=colander.Invalid,
    permission=NO_PERMISSION_REQUIRED,
    http_cache=0,
)
def handle_error_400_colander_invalid(error, request):
    """Return 400 JSON error."""
    errors = []
    for path, description in error.asdict().items():
        errors.append(('body', path, description))
    return _JSONError(errors, 400)


@view_config(
    context=Exception,
    permission=NO_PERMISSION_REQUIRED,
    http_cache=0,
)
def handle_error_500_exception(error, request):
    """Return 500 JSON error."""
    error = internal_exception_to_tuple(error)
    logger.exception('internal')
    return _JSONError([error], 500)


def internal_exception_to_tuple(error: Exception) -> tuple:
    """Convert an internal (unexpected) exception into a tuple."""
    args = str(error.args)
    msg = getattr(error, 'msg', '')
    return 'internal', args, msg


def includeme(config):  # pragma: no cover
    """Include pyramid configuration."""
    config.scan('.exceptions')
