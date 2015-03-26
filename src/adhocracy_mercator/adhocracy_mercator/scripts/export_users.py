"""Export scripts for adhocracy_mercator."""

import csv
import inspect
import optparse
import os
import sys
import textwrap
import time
import itertools
from pyramid.paster import bootstrap
from substanced.util import find_catalog

from adhocracy_core.catalog.adhocracy import index_rates
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


def _get_most_rated_proposals(root, min_rate=100):
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


def _get_proposals_titles(proposals):
    return [get_sheet_field(p, ITitle, 'title') for p in proposals]


def _get_rate_subject_name(rate):
    rater = get_sheet_field(rate, IRate, 'subject')
    return get_sheet_field(rater, IUserBasic, 'name')


def _get_user_rate(user_name, proposal):
    rates = get_sheet_field(proposal, IRateable, 'rates')
    last_rates = filter_by_tag(rates, 'LAST')
    rated = [get_sheet_field(rate, IRate, 'rate') for rate in last_rates
             if _get_rate_subject_name(rate) == user_name]
    if len(rated) == 1:
        return rated[0]
    return 0


def export_users():
    """Export all users from database and write them to csv file. """
    usage = 'usage: %prog config_file'
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(inspect.getdoc(export_users))
    )
    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 1:
        print('You must provide at least one argument')
        return 2

    env = bootstrap(args[0])

    root = (env['root'])
    catalog = find_catalog(root, 'system')
    path = catalog['path']
    interfaces = catalog['interfaces']

    query = path.eq('/principals/users/') \
        & interfaces.eq(IUser)

    users = query.execute()

    # FIXME: set 100 instead of 0 on prod
    proposals = _get_most_rated_proposals(root, 0)
    proposals_titles = _get_proposals_titles(proposals)
    proposals_column_names = zip(proposals_titles, itertools.repeat('Rate'))

    if not os.path.exists('./var/export/'):
        os.makedirs('./var/export/')

    timestr = time.strftime('%Y%m%d-%H%M%S')

    filename = './var/export/adhocracy-users-%s.csv' % timestr
    result_file = open(filename, 'w', newline='')
    wr = csv.writer(result_file, delimiter=';', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)
    columns = ['Username', 'Email', 'Creation date'] +\
        list(itertools.chain(*proposals_column_names))
    wr.writerow(columns)

    for user in users:
        user_name = get_sheet_field(user, IUserBasic, 'name')
        user_email = get_sheet_field(user, IUserExtended, 'email')
        creation_date = get_sheet_field(user, IMetadata, 'creation_date')
        formated_creation_date = creation_date.strftime('%Y-%m-%d_%H:%M:%S')

        row = [user_name, user_email, formated_creation_date]

        for proposal in proposals:
            user_rate = _get_user_rate(user_name, proposal)
            proposal_title = get_sheet_field(proposal, ITitle, 'title')

            row.append(proposal_title)
            row.append(user_rate)

        wr.writerow(row)

    env['closer']()
    print('Users exported to %s' % filename)


export_users()
