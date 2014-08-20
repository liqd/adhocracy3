"""Rest API exceptions."""
import logging

from cornice.util import _JSONError
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
import colander

from adhocracy.rest.views import cache_max_seconds


logger = logging.getLogger(__name__)


@view_config(
    context=colander.Invalid,
    permission=NO_PERMISSION_REQUIRED,
    http_cache=cache_max_seconds,
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
    http_cache=cache_max_seconds,
)
def handle_error_500_exception(error, request):
    """Return 500 JSON error."""
    args = str(error.args)
    msg = getattr(error, 'msg', '')
    error = ('internal', args, msg)
    logger.exception('internal')
    return _JSONError([error], 500)


def includeme(config):  # pragma: no cover
    """Include pyramid configuration."""
    config.scan('.exceptions')
