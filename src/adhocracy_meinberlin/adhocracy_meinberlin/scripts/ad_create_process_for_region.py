"""Script to create Process for region."""

import sys
import argparse
import textwrap
import inspect

from pyramid.paster import bootstrap
from pyramid.traversal import find_resource

import transaction

from adhocracy_core.sheets.pool import IPool
from adhocracy_core.sheets.geo import IMultiPolygon
from adhocracy_core.sheets.name import IName
from adhocracy_core.sheets.title import ITitle

from adhocracy_meinberlin.resources.kiezkassen import IProcess
from adhocracy_core.sheets.geo import ILocationReference


def main():
    """Create sample Kiezkassen process for a given region and organisation."""
    doc = textwrap.dedent(inspect.getdoc(main))
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('config')
    parser.add_argument('region_name')
    parser.add_argument('organisation_name')
    args = parser.parse_args()

    env = bootstrap(args.config)
    root = env['root']
    registry = env['registry']

    district = _fetch_district_by_name(root, args.region_name, registry)
    organisation = _fetch_organisation_by_name(root, args.organisation_name)

    _create_process(root, registry, organisation, district)


def _fetch_district_by_name(root, district, registry):
    pool = registry.content.get_sheet(root, IPool)
    params = {'depth': 3,
              'interfaces': IMultiPolygon,
              }
    results = pool.get(params)
    locations = results['elements']
    for location in locations:
        name = registry.content.get_sheet_field(location, IName, 'name')
        if name == district:
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

    name = registry.content.get_sheet_field(district, IName, 'name')
    title = registry.content.get_sheet_field(district, ITitle, 'title')

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
