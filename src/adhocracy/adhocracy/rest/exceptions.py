from cornice.util import _JSONError
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

import colander


@view_config(
    context=colander.Invalid,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_400_colander_invalid(error, request):
    errors = []
    for path, description in error.asdict().items():
        errors.append(('body', path, description))
    return _JSONError(errors, 400)


@view_config(
    context=Exception,
    permission=NO_PERMISSION_REQUIRED,
)
def handle_error_500_exception(error, request):
    args = str(error.args)
    msg = getattr(error, "msg", "")
    error = ('internal', args, msg)
    return _JSONError([error], 500)
