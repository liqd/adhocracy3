"""Export users and their proposal rates.

This is registered as console script 'export_mercator_users' in setup.py.

"""

import argparse
import csv
import inspect
from pyramid.paster import bootstrap
from substanced.util import find_service

from adhocracy_core.interfaces import IResource
from adhocracy_core.resources.principal import IUser
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.rate import IRate
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import create_filename
from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
from adhocracy_mercator.sheets.mercator import ITitle
from adhocracy_core.sheets.pool import IPool


def export_users():
    """Export all users and their proposal rates to csv file.

    usage::

        bin/export_mercator_users etc/development.ini  10
    """
    docstring = inspect.getdoc(export_users)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('min_rate',
                        type=int,
                        help='minimal rate to restrict listed proposals')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    filename = create_filename(directory='./var/export/',
                               prefix='adhocracy-users',
                               suffix='.csv')
    _export_users_and_proposals_rates(env['root'], filename,
                                      min_rate=args.min_rate)
    env['closer']()


def _export_users_and_proposals_rates(root: IResource, filename: str,
                                      min_rate=0):
    proposals = get_most_rated_proposals(root, min_rate)
    proposals_titles = get_titles(proposals)
    column_names = ['Username', 'Email', 'Creation date'] + proposals_titles
    with open(filename, 'w', newline='') as result_file:
        wr = csv.writer(result_file, delimiter=';', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
        wr.writerow(column_names)
        users = _get_users(root)
        proposals_users_map = _map_rating_users(proposals)
        for pos, user in enumerate(users):
            row = []
            _append_user_data(user, row)
            _append_rate_dates(user, proposals_users_map, row)
            wr.writerow(row)
            print('exported user {0} of {1}'.format(pos, len(users)))
    print('Users exported to {0}'.format(filename))


def get_titles(resources: [ITitle]) -> [str]:
    """Return all titles for `resources`."""
    titles = [get_sheet_field(p, ITitle, 'title') for p in resources]
    return titles


def _get_users(root: IResource) -> [IUser]:
    users = find_service(root, 'principals', 'users')
    return users.values()


def get_most_rated_proposals(root: IResource,
                             min_rate: int) -> [IMercatorProposalVersion]:
    """Return child proposals of `root` with rating higher then `min_rate`."""
    pool = get_sheet(root, IPool)
    params = {'depth': 3,
              'content_type': IMercatorProposalVersion,
              'sort': 'rates',
              'reverse': True,
              'tag': 'LAST',
              'aggregateby': 'rates',
              'aggregateby_elements': 'content',
              'elements': 'content',
              }
    results = pool.get(params)
    proposals = results['elements']
    aggregates = results['aggregateby']['rates']
    # remove proposals with rate < min_rate.
    # TODO extend query parameters to allow comparators, like
    # 'rate': '>=3'
    for rate, aggregated_proposals in aggregates.items():
        if int(rate) < min_rate:
            for p in aggregated_proposals:
                try:
                    proposals.remove(p)
                except ValueError:
                    pass
    return proposals


def _map_rating_users(rateables: [IRateable]) -> [(IRateable, set(IUser))]:
    rateables_users_map = []
    for rateable in rateables:
        params = {'depth': 3,
                  'content_type': IRate,
                  'tag': 'LAST',
                  'rate': 1,
                  'elements': 'content',
                  IRate.__identifier__ + ':object': rateable,
                  }
        pool = get_sheet(rateable.__parent__, IPool)
        rates = pool.get(params)['elements']
        users = [get_sheet_field(x, IRate, 'subject') for x in rates]
        rateables_users_map.append((rateable, set(users)))
    return rateables_users_map


def _append_user_data(user: IUser, row: [str]):
    name = get_sheet_field(user, IUserBasic, 'name')
    email = get_sheet_field(user, IUserExtended, 'email')
    creation_date = get_sheet_field(user, IMetadata, 'creation_date')
    creation_date_str = creation_date.strftime('%Y-%m-%d_%H:%M:%S')
    row.extend([name, email, creation_date_str])


def _append_rate_dates(user: IUser, rateables: [(IRateable, set(IUser))],
                       row: [str]):
    for rateable, users in rateables:
        date = ''
        if user in users:
            date = _get_rate_date(user, rateable)
        row.append(date)


def _get_rate_date(user: IUser, rateable: IRateable) -> str:
    pool = get_sheet(rateable.__parent__, IPool)
    params = {'depth': 3,
              'content_type': IRate,
              'tag': 'LAST',
              IRate.__identifier__ + ':subject': user,
              IRate.__identifier__ + ':object': rateable,
              'rate': 1,
              'elements': 'content',
              'count': True
              }
    result = pool.get(params)
    rate = result['elements'][0]
    creation_date = get_sheet_field(rate, IMetadata, 'item_creation_date')
    creation_date_str = creation_date.strftime('%Y-%m-%d_%H:%M:%S')
    return creation_date_str
