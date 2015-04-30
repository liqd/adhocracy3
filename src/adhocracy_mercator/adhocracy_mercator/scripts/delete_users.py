"""Delete users whose emails are listed in a file.

Votes from the users are also deleted.

This script is registered as console script 'delete_users' in
setup.py.

"""

import argparse
import inspect
import transaction
from pyramid.paster import bootstrap

from adhocracy_core.interfaces import IResource
from substanced.interfaces import IUserLocator
from adhocracy_core.resources.principal import IUser
from adhocracy_core.resources.rate import IRateVersion
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.sheets.rate import IRate
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_sheet_field
from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
from pyramid.request import Request
from pyramid.registry import Registry


def delete_users():
    """Delete users whose emails are listed in a file.

    usage::

         bin/delete_users etc/development.ini <filename>
    """
    docstring = inspect.getdoc(delete_users)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('filename',
                        type=str,
                        help='filename containing an email per line')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    root = env['root']
    registry = env['registry']
    _delete_users_and_votes(args.filename, root, registry)
    env['closer']()


def _delete_users_and_votes(filename: str, root: IResource, registry: Registry):
    print('Reading emails from file...')
    users_emails = _get_emails(filename)
    print('Getting users from the database...')
    users = _get_users(root, registry, users_emails)
    pool = get_sheet(root, IPool)
    for user in users:
        user_name = user.__name__
        _delete_proposals_rates(pool, user)
        _delete_user(user)
        print('User {} and its votes deleted.'.format(user_name))
    transaction.commit()
    print('Users deleted successfully.')


def _delete_proposals_rates(pool: IPool, user: IUser):
    rates = _get_rates_from_user(pool, user)
    proposals_rates = _select_proposal_rates(rates)
    for proposal_rate in proposals_rates:
        proposal_rate.__parent__.remove(proposal_rate.__name__)


def _delete_user(user: IUser):
    user.__parent__.remove(user.__name__)


def _get_users(root: IResource, registry: Registry, emails: [str]) -> [IUser]:
    locator = _get_user_locator(root, registry)
    for email in emails:
        user = locator.get_user_by_email(email)
        if user is None:
            print('No user found for email: ', email)
        else:
            yield user


def _get_emails(filename: str) -> [str]:
    return [line.rstrip() for line in open(filename)]


def _get_user_locator(context: IResource, registry: Registry) -> IUserLocator:
    request = Request.blank('/dummy')
    locator = registry.getMultiAdapter((context, request), IUserLocator)
    return locator


def _get_rates_from_user(pool: IPool, user: IUser) -> [IRateVersion]:
    params = {'depth': 6,
              'content_type': IRate,
              'elements': 'content',
              IRate.__identifier__ + ':subject': user,
              }
    rates = pool.get(params)['elements']
    return rates


def _select_proposal_rates(rates: [IRateVersion]) -> [IRateVersion]:
    return [rate for rate in rates
            if IMercatorProposalVersion.providedBy(get_sheet_field(rate, IRate, 'object'))]
