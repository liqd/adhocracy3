"""Delete users whose emails are listed in a file.

Votes from the users are also deleted.

This script is registered as console script 'delete_users' in
setup.py.

"""

import argparse
import inspect
from pyramid.paster import bootstrap

from adhocracy_core.interfaces import IResource
from substanced.interfaces import IUserLocator
from adhocracy_core.resources.principal import IUser
from adhocracy_core.resources.rate import IRateVersion
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.sheets.rate import IRate
# from adhocracy_core.sheets.rate import IRateable
# from adhocracy_core.utils import get_sheet
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
    users_emails = _get_emails(filename)
    users = _get_users(root, registry, users_emails)
    print('users=', users)
    return users


def _get_users(root: IResource, registry: Registry, emails: [str]) -> [IUser]:
    locator = _get_user_locator(root, registry)
    return [locator.get_user_by_email(email) for email in emails]


def _get_emails(filename: str) -> [str]:
    return ['user1@example.com']


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


def _select_proposal_rates_(rates: [IRateVersion]) -> [IRateVersion]:
    return [rate for rate in rates
            if IMercatorProposalVersion.providedBy(get_sheet_field(rate, IRate, 'object'))]

#
# get_sheet(rvs[0], adhocracy_core.sheets.rate.IRate).get()
# deletion
# rv0.__parent__.remove(rv0.__name__)

# from adhocracy_mercator.scripts.delete_users import _delete_users_and_votes
# from adhocracy_mercator.scripts.delete_users import _get_rates_from_user
# from adhocracy_core.sheets.pool import IPool
# from adhocracy_core.sheets.rate import IRate
# from adhocracy_core.utils import get_sheet
# from adhocracy_core.utils import get_isheets
# import transaction
#
# users = _delete_users_and_votes('', root, registry)
# u1 = users[0]
# pool = get_sheet(root, IPool)
# rvs =  _get_rates_from_user(pool, u1)
# rv0 = rvs[0]
# rate0 = get_sheet(rv0, IRate)
