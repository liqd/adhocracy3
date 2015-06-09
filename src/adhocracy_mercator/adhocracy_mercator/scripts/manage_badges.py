"""Assign badges to proposals.

The functions of that script are registered as console script in
setup.py.

"""

import inspect
import argparse
import transaction

from pyramid.paster import bootstrap
from pyramid.traversal import find_resource
from substanced.util import find_service
from adhocracy_core.utils import load_json
from adhocracy_core.resources.badge import IBadgeAssignment as BadgeRessource
from adhocracy_core.sheets.badge import IBadgeAssignment as BadgeSheet


def add_badge_assignment_from_json():
    """add badgeassignment.

    usage::
      bin/create_badge <config> <jsonfile>
    """
    args = _create_parser()
    env = bootstrap(args.ini_file)
    root = env['root']
    registry = env['registry']

    entries = load_json(args.jsonfile)

    for entry in entries:
        _create_badge_assignment(entry, root, registry)

    transaction.commit()
    env['closer']()


def _create_appstructs(subject, badge, object, description):

    appstructs = {BadgeSheet.__identifier__:
                  {'subject': subject,
                   'badge': badge,
                   'object': object,
                   'description': description}}

    return appstructs


def _get_resources(
        root,
        userpath,
        badgepath,
        proposalversionpath,
        proposalitempath):

    user = find_resource(root, userpath)
    badge = find_resource(root, badgepath)
    proposal_version = find_resource(root, proposalversionpath)
    proposal_item = find_resource(root, proposalitempath)
    return user, badge, proposal_version, proposal_item


def _create_badge_assignment(entry, root, registry):

    user = entry['user']
    badge = entry['badge']
    proposalversion = entry['proposalversion']
    proposalitem = entry['proposalitem']
    user, badge, proposal_version, parent = _get_resources(
        root, user, badge, proposalversion, proposalitem)

    description = entry['description']
    service = find_service(parent, 'badge_assignments')
    appstructs = _create_appstructs(user, badge, proposal_version, description)

    registry.content.create(BadgeRessource.__identifier__,
                            parent=service,
                            appstructs=appstructs)


def _create_parser():
    docstring = inspect.getdoc(add_badge_assignment_from_json)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('jsonfile',
                        type=str,
                        help='path to jsonfile')

    return parser.parse_args()
