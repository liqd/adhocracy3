"""Delete users whose emails are listed in a file.

Votes from the users are also deleted.

This script is registered as console script 'delete_users' in
setup.py.

"""

import argparse
import inspect
import transaction
from pyramid.paster import bootstrap
from pyramid.request import Request
from pyramid.registry import Registry
from substanced.util import find_service

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import search_query
from substanced.interfaces import IUserLocator
from adhocracy_core.catalog import ICatalogsService
from adhocracy_core.resources.principal import IUser
from adhocracy_core.resources.rate import IRate
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_mercator.scripts.export_users import get_most_rated_proposals


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


def _delete_users_and_votes(filename: str, root: IPool,
                            registry: Registry):
    print('Reading emails from file...')
    users_emails = _get_emails(filename)
    print('Getting users from the database...')
    users = _get_users(root, registry, users_emails)
    catalogs = find_service(root, 'catalogs')
    index = 1
    for user in users:
        print('Deleting user {} ({}) and its rates'.format(user.__name__,
                                                           user.email))
        _delete_rate_items(catalogs, user)
        _delete(user)
        if index % 100 == 0:
            print('Creating savepoint...')
            transaction.savepoint()
        index = index + 1
    print('Reindexing...')
    _reindex_proposals(catalogs, root)
    print('Committing changes...')
    transaction.commit()
    print('Users deleted successfully.')


def _reindex_proposals(catalogs: ICatalogsService, root: IPool):
    proposals = get_most_rated_proposals(root, min_rate=0)
    for proposal in proposals:
        catalogs.reindex_index(proposal, 'rates')


def _delete_rate_items(catalogs: ICatalogsService, user: IUser):
    query = search_query._replace(
        interfaces=IRate,
        references=[(None, IMetadata, 'creator', user)],
    )
    user_rates = catalogs.search(query).elements
    for rate in user_rates:
        _delete(rate)


def _delete(resource: IResource):
    resource.__parent__.remove(resource.__name__)


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
