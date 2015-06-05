"""Assign badges to proposals.

The functions of that script are registered as console script in
setup.py.

"""

import inspect
import optparse
import sys
import textwrap
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
    usage = 'usage: %prog config_file user badge proposal parent'
    description = textwrap.dedent(inspect.getdoc(add_badge_assignment))
    parser = optparse.OptionParser(
        usage=usage,
        description=description
    )

    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 5:
        print('You must provide five arguments')
        return 5

    env = bootstrap(args[0])
    root = env['root']
    registry = env['registry']

    user = args[1]
    badge = args[2]
    proposal_version = args[3]
    parent = args[4]

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
    usage = 'usage: %prog config_file jsonfile'
    description = inspect.getdoc(add_badge_assignment_from_json)
    description = textwrap.dedent(description)
    parser = optparse.OptionParser(
        usage=usage,
        description=description
    )

    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 2:
        print('You must provide two arguments')
        return 2

    env = bootstrap(args[0])
    root = env['root']
    registry = env['registry']

    entries = _load_json(args[1])

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
