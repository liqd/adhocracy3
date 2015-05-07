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
from substanced.util import find_catalog


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
    modified_proposals = set()
    index = 1
    for user in users:
        user_name = user.__name__
        user_email = user.email
        currently_modified = _delete_proposals_rates(pool, user)
        modified_proposals.update(currently_modified)
        _delete_user(user)
        if index % 100 == 0:
            print('Creating savepoint...')
            transaction.savepoint()
        index = index + 1
        print('User {} ({}) and its votes deleted.'.format(user_name, user_email))
    print('Reindexing...')
    _reindex_proposals(root, modified_proposals)
    print('Committing changes...')
    transaction.commit()
    print('Users deleted successfully.')


def _reindex_proposals(pool: IPool, proposals: [IMercatorProposalVersion]):
    adhocracy = find_catalog(pool, 'adhocracy')
    rates = adhocracy['rates']
    for proposal in proposals:
        rates.reindex_resource(proposal)


def _delete_proposals_rates(pool: IPool, user: IUser) -> [IMercatorProposalVersion]:
    """Return the list of modified proposals."""
    rates = _get_rates_from_user(pool, user)
    proposals_rates = _select_proposal_rates(rates)
    modified = [get_sheet_field(proposal_rate, IRate, 'object')
                for proposal_rate in proposals_rates]
    for proposal_rate in proposals_rates:
        proposal_rate.__parent__.remove(proposal_rate.__name__)
    return modified


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
              'interfaces': IRate,
              'resolve': True,
              'arbitrary_indexes': {'tag': 'LAST'},
              'references': [(None, IRate, 'subject', user)],
              }
    rates = pool.get(params)['elements']
    return rates


def _select_proposal_rates(rates: [IRateVersion]) -> [IRateVersion]:
    return [rate for rate in rates
            if IMercatorProposalVersion.providedBy(get_sheet_field(rate, IRate, 'object'))]
