"""Assign badges to proposals.

The functions of that script are registered as console script in
setup.py.

"""

import inspect
import optparse
import sys
import textwrap
import transaction

from pyramid.paster import bootstrap
from pyramid.traversal import find_resource
from adhocracy_core.resources.badge import IBadgeAssignment as BadgeResource
from adhocracy_core.sheets.badge import IBadgeAssignment as BadgeSheet


def add_badge_assignment():
    """add badgeassignment.

    usage::
      bin/create_badge <config> <user> <badge> <proposal> <parent>
    """
    usage = 'usage: %prog config_file region organisation'
    description = textwrap.dedent(inspect.getdoc(add_badge_assignment))
    parser = optparse.OptionParser(
        usage=usage,
        description=description
    )

    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 4:
        print('You must provide four arguments')
        return 4

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
