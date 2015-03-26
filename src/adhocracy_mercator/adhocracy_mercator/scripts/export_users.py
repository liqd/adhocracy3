"""Export scripts for adhocracy_mercator."""

import csv
import inspect
import optparse
import os
import sys
import textwrap
import time

from pyramid.paster import bootstrap
from substanced.util import find_catalog

from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.utils import get_sheet_field

from adhocracy_core.resources.principal import IUser


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

    if not os.path.exists('./var/export/'):
        os.makedirs('./var/export/')

    timestr = time.strftime('%Y%m%d-%H%M%S')

    filename = './var/export/adhocracy-users-%s.csv' % timestr
    result_file = open(filename, 'w', newline='')
    wr = csv.writer(result_file, delimiter=';', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)
    wr.writerow(['Username', 'Email', 'Creation date'])

    for user in users:
        user_name = get_sheet_field(user, IUserBasic, 'name')
        user_email = get_sheet_field(user, IUserExtended, 'email')
        creation_date = get_sheet_field(user, IMetadata, 'creation_date')
        formated_creation_date = creation_date.strftime('%Y-%m-%d_%H:%M:%S')

        wr.writerow([user_name, user_email, formated_creation_date])

    env['closer']()
    print('Users exported to %s' % filename)


export_users()
