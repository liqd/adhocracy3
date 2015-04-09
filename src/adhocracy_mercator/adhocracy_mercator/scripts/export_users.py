"""Export users and their proposal rates.

This is registered as console script 'export_mercator_users' in setup.py.

"""

import argparse
import csv
import inspect
import os
import time
from pyramid.paster import bootstrap
from pyramid.registry import Registry
from substanced.util import find_catalog
from substanced.util import find_service

from adhocracy_core.catalog.adhocracy import index_rates
from adhocracy_core.interfaces import IResource
from adhocracy_core.resources.principal import IUser
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.rate import IRate
from adhocracy_core.utils import get_sheet_field
from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
from adhocracy_mercator.sheets.mercator import ITitle
from adhocracy_core.sheets.tags import filter_by_tag


def create_filename(dir='.', prefix='', suffix='') -> str:
    """Use current time to create unique filename.

    :params dir: directory path for the filename.
                 If non existing the directory is created.
    :params prefix: prefix for the generated name
    :params suffix: type suffix for the generated name, like 'csv'
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
    timestr = time.strftime('%Y%m%d-%H%M%S')
    name = '{0}-{1}.{2}'.format(prefix, timestr, suffix)
    path = os.path.join(dir, name)
    return path


def export_users():
    """Export all users and their proposal rates to csv file.

    usage::

        bin/export_mercator_users etc/development.ini  10
    """
    docstring = inspect.getdoc(export_users)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backendini file')
    parser.add_argument('min_rate',
                        type=int,
                        help='minimal rate to restrict listed proposals')
    filename = create_filename(dir='./var/export/',
                               prefix='adhocracy-users',
                               suffix='csv')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    _export_users(env['root'], env['registry'], filename,
                  min_rate=args.min_rate)
    env['closer']()


def _export_users(root: IResource, registry: Registry, filename: str,
                  min_rate=0):
    users = _get_users(root)
    proposals = _get_most_rated_proposals(root, min_rate=min_rate)
    proposals_titles = _get_titles(proposals)
    columns = ['Username', 'Email', 'Creation date'] + proposals_titles
    with open(filename, 'w', newline='') as result_file:
        wr = csv.writer(result_file, delimiter=';', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
        wr.writerow(columns)
        for user in users:
            row = []
            _append_user_data(user, row)
            _append_proposals_rate(user, proposals, row)
            wr.writerow(row)
    print('Users exported to %s' % filename)


def _get_users(root: IResource) -> [IUser]:
    users = find_service(root, 'principals', 'users')
    return users.values()


def _get_most_rated_proposals(root: IResource, min_rate=0):
    catalog = find_catalog(root, 'system')
    adhocracy_catalog = find_catalog(root, 'adhocracy')
    path = catalog['path']
    interfaces = catalog['interfaces']
    tag = adhocracy_catalog['tag']

    query = path.eq('/mercator') \
        & interfaces.eq(IMercatorProposalVersion) \
        & tag.eq('LAST')

    proposals = query.execute()
    proposals = [p for p in proposals if index_rates(p, None) > min_rate]
    proposals = list(reversed(sorted(proposals,
                                     key=lambda p: index_rates(p, None))))
    return proposals


def _get_titles(proposals: [ITitle]) -> [str]:
    return [get_sheet_field(p, ITitle, 'title') for p in proposals]


def _append_user_data(user: IUser, row: list):
            name = get_sheet_field(user, IUserBasic, 'name')
            email = get_sheet_field(user, IUserExtended, 'email')
            creation_date = get_sheet_field(user, IMetadata, 'creation_date')
            creation_date_str = creation_date.strftime('%Y-%m-%d_%H:%M:%S')
            row.extend([name, email, creation_date_str])


def _append_proposals_rate(user: IUser, proposals: list, row: list):
        for proposal in proposals:
            rate, date = _get_user_rate(user.__name__, proposal)
            row.append(date)


def _get_user_rate(user_name: str, proposal: IRateable) -> (int, str):
    rates = get_sheet_field(proposal, IRateable, 'rates')
    last_rates = filter_by_tag(rates, 'LAST')
    rated = [rate for rate in last_rates
             if _get_rate_subject_name(rate) == user_name]

    if len(rated) == 1:
        rate = rated[0]
        creation_date = get_sheet_field(rate, IMetadata, 'item_creation_date')
        return (get_sheet_field(rate, IRate, 'rate'),
                creation_date.strftime('%Y-%m-%d_%H:%M:%S'))
    return 0, ''


def _get_rate_subject_name(rate: IRate):
    rater = get_sheet_field(rate, IRate, 'subject')
    return get_sheet_field(rater, IUserBasic, 'name')
