"""Export users and their proposal rates.

This is a generic script used for diffrerent proposal implementations.
"""

import csv
from pyramid.registry import Registry
from substanced.util import find_service

from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import search_query
from adhocracy_core.resources.principal import IUser
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.rate import IRate
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.principal import IPasswordAuthentication


def export_users_and_proposals_rates(root: IResource, filename: str,
                                     proposal_interface: IItem,
                                     registry: Registry, args):
    """Export all users and their proposal rates to csv file."""
    proposals = get_most_rated_proposals(root, args.min_rate,
                                         proposal_interface, registry)
    proposals_titles = get_titles(proposals, registry)
    if args.include_passwords:
        column_names = ['Username', 'Email', 'Creation date',
                        'Password Hash'] + proposals_titles
    else:
        column_names = ['Username', 'Email',
                        'Creation date'] + proposals_titles
    with open(filename, 'w', newline='') as result_file:
        wr = csv.writer(result_file, delimiter=';', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
        wr.writerow(column_names)
        users = _get_users(root)
        proposals_users_map = _map_rating_users(proposals, registry)
        for pos, user in enumerate(users):
            row = []
            _append_user_data(user, row, args.include_passwords, registry)
            _append_rate_dates(user, proposals_users_map, row, registry)
            wr.writerow(row)
            print('exported user {0} of {1}'.format(pos, len(users)))
    print('Users exported to {0}'.format(filename))


def get_titles(resources: [ITitle], registry: Registry) -> [str]:
    """Return all titles for `resources`."""
    titles = [registry.content.get_sheet_field(p, ITitle, 'title')
              for p in resources]
    return titles


def _get_users(root: IResource) -> [IUser]:
    users = find_service(root, 'principals', 'users')
    return [u for u in users.values() if IUser.providedBy(u)]


def get_most_rated_proposals(root: IResource,
                             min_rate: int,
                             proposal_interface: IItem) -> [IItem]:
    """Return child proposals of `root` with rating higher then `min_rate`."""
    catalogs = find_service(root, 'catalogs')
    query = search_query._replace(interfaces=proposal_interface,
                                  resolve=True,
                                  group_by='rates',
                                  sort_by='rates',
                                  reverse=True
                                  )
    proposals = catalogs.search(query).elements
    aggregates = catalogs.search(query).group_by
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


def _map_rating_users(rateables: [IRateable],
                      registry: Registry) -> [(IRateable, set(IUser))]:
    rateables_users_map = []
    get_sheet_field = registry.content.get_sheet_field
    for rateable in rateables:
        catalogs = find_service(rateable, 'catalogs')
        references = [(None, IRate, 'object', rateable)]
        query = search_query._replace(interfaces=IRate,
                                      resolve=True,
                                      references=references
                                      )
        rates = catalogs.search(query).elements
        users = [get_sheet_field(x, IRate, 'subject') for x in rates]
        rateables_users_map.append((rateable, set(users)))
    return rateables_users_map


def _append_user_data(user: IUser, row: [str], include_passwords: bool,
                      registry: Registry):
    get_sheet_field = registry.content.get_sheet_field
    name = get_sheet_field(user, IUserBasic, 'name')
    email = get_sheet_field(user, IUserExtended, 'email')
    creation_date = get_sheet_field(user, IMetadata, 'creation_date')
    creation_date_str = creation_date.strftime('%Y-%m-%d_%H:%M:%S')
    if include_passwords:
        passw = get_sheet_field(user, IPasswordAuthentication, 'password')
        row.extend([name, email, creation_date_str, passw])
    else:
        row.extend([name, email, creation_date_str])


def _append_rate_dates(user: IUser, rateables: [(IRateable, set(IUser))],
                       row: [str],
                       registry: Registry):
    for rateable, users in rateables:
        date = ''
        if user in users:
            date = _get_rate_date(user, rateable, registry)
        row.append(date)


def _get_rate_date(user: IUser,
                   rateable: IRateable,
                   registry: Registry) -> str:
    catalogs = find_service(rateable, 'catalogs')
    references = [(None, IRate, 'subject', user),
                  (None, IRate, 'object', rateable)]
    query = search_query._replace(interfaces=IRate,
                                  resolve=True,
                                  references=references
                                  )
    rate = catalogs.search(query).elements[0]
    creation_date = registry.content.get_sheet_field(rate,
                                                     IMetadata,
                                                     'item_creation_date')
    creation_date_str = creation_date.strftime('%Y-%m-%d_%H:%M:%S')
    return creation_date_str
