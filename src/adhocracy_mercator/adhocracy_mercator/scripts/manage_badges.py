"""Assign badges to proposals.

The functions of that script are registered as console script in
setup.py.

"""

import inspect
import argparse
import transaction
import json

from pyramid.paster import bootstrap
from pyramid.traversal import find_resource
from adhocracy_core.resources.badge import IBadgeAssignment as BadgeResource
from adhocracy_core.sheets.badge import IBadgeAssignment as BadgeSheet


def add_badge_assignment():
    """add badgeassignment.

    usage::
      bin/create_badge <config> <user> <badge> <proposal> <parent>
    """
    docstring = inspect.getdoc(add_badge_assignment)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('user',
                        type=str,
                        help='path to user')
    parser.add_argument('badge',
                        type=str,
                        help='path to badge')
    parser.add_argument('proposal',
                        type=str,
                        help='path to proposal')
    parser.add_argument('parent',
                        type=str,
                        help='path to parent')

    args = parser.parse_args()
    env = bootstrap(args.ini_file)

    root = env['root']
    registry = env['registry']

    user = args.user
    badge = args.badge
    proposal_version = args.proposal
    parent = args.parent

    user = find_resource(root, user)
    badge = find_resource(root, badge)
    proposal_version = find_resource(root, proposal_version)
    parent = find_resource(root, parent)

    appstructs = {BadgeSheet.__identifier__:
                  {'subject': user,
                   'badge': badge,
                   'object': proposal_version}}

    registry.content.create(BadgeResource.__identifier__,
                            parent=parent,
                            appstructs=appstructs)

    transaction.commit()


def add_badge_assignment_from_json():
    """add badgeassignment.

    usage::
      bin/create_badge <config> <jsonfile>
    """
    docstring = inspect.getdoc(add_badge_assignment)
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

    entries = _load_json(args.jsonfile)

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

        registry.content.create(BadgeResource.__identifier__,
                                parent=parent,
                                appstructs=appstructs)

    transaction.commit()


def _load_json(filename: str) -> [dict]:
    with open(filename, 'r') as f:
        return json.load(f)
