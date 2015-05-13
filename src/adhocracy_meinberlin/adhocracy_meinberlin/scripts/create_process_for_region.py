"""Create Process for region."""

import sys
import optparse
import textwrap
import inspect

from pyramid.paster import bootstrap
from pyramid.traversal import find_resource

import transaction

from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.sheets.geo import IMultiPolygon
from adhocracy_core.sheets.name import IName
from adhocracy_core.sheets.title import ITitle

from adhocracy_meinberlin.resources.kiezkassen import IProcess
from adhocracy_core.sheets.geo import ILocationReference


def create_process_for_region():
    """Create sample Kiezkassen process for a given region and organisation.

    usage::

      bin/create_process_for_region <config> <regionname> <organisationname>
    """
    usage = 'usage: %prog config_file region organisation'
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(inspect.getdoc(create_process_for_region))
    )
    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 3:
        print('You must provide at least three argument')
        return 2

    env = bootstrap(args[0])
    root = env['root']
    registry = env['registry']

    district = _fetch_district_by_name(root, args[1])
    organisation = _fetch_organisation_by_name(root, args[2])

    _create_process(root, registry, organisation, district)


def _fetch_district_by_name(root, district):
    pool = get_sheet(root, IPool)
    params = {'depth': 3,
              'interfaces': IMultiPolygon
              }
    results = pool.get(params)
    locations = results['elements']
    for location in locations:
        if get_sheet_field(location, IName, 'name') == district:
            return location

    print('could not find district %s' % (district))
    sys.exit()


def _fetch_organisation_by_name(root, organisation_path):
    organisation = find_resource(root, organisation_path)
    if organisation is None:
        print('could not find organisation %s' % (organisation))
        sys.exit()
    else:
        return organisation


def _create_process(root, registry, organisation, district):

    name = get_sheet_field(district, IName, 'name')
    title = get_sheet_field(district, ITitle, 'title')

    appstructs = {IName.__identifier__:
                  {'name': name},
                  ITitle.__identifier__:
                  {'title': 'Kiezkasse für %s' % (title)},
                  ILocationReference.__identifier__:
                  {'location': district}
                  }

    registry.content.create(IProcess.__identifier__,
                            parent=root['organisation'],
                            appstructs=appstructs)

    transaction.commit()
