"""Assign badges to proposals.

The functions of that script are registered as console script in
setup.py.

"""

import inspect
import argparse
import transaction

from pyramid.paster import bootstrap
from pyramid.traversal import find_resource
from adhocracy_core.utils import load_json
from adhocracy_core.resources.badge import IBadgeAssignment as BadgeRessource
from adhocracy_core.sheets.badge import IBadgeAssignment as BadgeSheet


def add_badge_assignment_from_json():
    """add badgeassignment.

    usage::
      bin/create_badge <config> <jsonfile>
    """
    docstring = inspect.getdoc(add_badge_assignment_from_json)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('jsonfile',
                        type=str,
                        help='path to jsonfile')

    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    root = env['root']
    registry = env['registry']

    entries = load_json(args.jsonfile)

    for entry in entries:
        user = find_resource(root, entry['user'])
        badge = find_resource(root, entry['badge'])
        proposal_version = find_resource(root, entry['proposalversion'])
        parent = find_resource(root, entry['proposalitem'])
        description = entry['description']

        appstructs = {BadgeSheet.__identifier__:
                      {'subject': user,
                       'badge': badge,
                       'object': proposal_version,
                       'description': description}}

        registry.content.create(BadgeRessource.__identifier__,
                                parent=parent,
                                appstructs=appstructs)

    transaction.commit()
    env['closer']()



