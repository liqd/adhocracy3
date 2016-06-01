"""Script to delete stale login data."""
import transaction
import argparse
import inspect
import logging

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.paster import bootstrap
from pyramid.request import Request

from adhocracy_core.authentication import get_tokenmanager
from adhocracy_core.resources.principal import delete_password_resets
from adhocracy_core.resources.principal import delete_not_activated_users


logger = logging.getLogger(__name__)


def main():  # pragma: no cover
    """Remove expired login tokens, not active users, old password resets."""
    docstring = inspect.getdoc(main)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('-r',
                        '--resets_max_age',
                        help='Max age in days for unused password resets',
                        default=30,
                        type=int)
    parser.add_argument('-u',
                        '--not_active_users_max_age',
                        help='Max age in days for not activated users',
                        default=60,
                        type=int)
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    delete_stale_login_data(env['root'],
                            env['request'],
                            args.resets_max_age,
                            args.not_active_users_max_age,
                            )
    transaction.commit()
    env['closer']()


def delete_stale_login_data(root,
                            request: Request,
                            not_active_users_max_age: int,
                            resets_max_age: int,
                            ):
    """Remove expired login tokens, not active users, old password resets."""
    request.root = root
    delete_not_activated_users(request, not_active_users_max_age)
    delete_password_resets(request, resets_max_age)
    auth = request.registry.queryUtility(IAuthenticationPolicy)
    token_manger = get_tokenmanager(request)
    if token_manger:  # pragma: no branch
        token_manger.delete_expired_tokens(auth.timeout)
