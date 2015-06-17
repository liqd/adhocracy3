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

from adhocracy_core import resources
from adhocracy_core import sheets
from adhocracy_core.utils import load_json


def assign_badges():  # pragma: no cover
    """Assign badges to proposals.

    usage::
      bin/assign_badges <config> <jsonfile>
    """
    args = _parse_args()
    env = bootstrap(args.ini_file)
    root = env['root']
    registry = env['registry']

    entries = load_json(args.jsonfile)

    for entry in entries:
        _create_badge_assignment(entry, root, registry)

    transaction.commit()
    env['closer']()


def _parse_args():  # pragma: no cover
    docstring = inspect.getdoc(assign_badges)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('jsonfile',
                        type=str,
                        help='path to jsonfile')

    return parser.parse_args()


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

    registry.content.create(resources.badge.IBadgeAssignment.__identifier__,
                            parent=service,
                            appstructs=appstructs)


def _create_appstructs(subject, badge, object, description):
    appstructs = {sheets.badge.IBadgeAssignment.__identifier__:
                  {'subject': subject,
                   'badge': badge,
                   'object': object
                   },
                  sheets.description.IDescription.__identifier__:
                  {'description': description}
                  }
    return appstructs


def _get_resources(root, userpath, badgepath, proposalversionpath,
                   proposalitempath):
    user = find_resource(root, userpath)
    badge = find_resource(root, badgepath)
    proposal_version = find_resource(root, proposalversionpath)
    proposal_item = find_resource(root, proposalitempath)
    return user, badge, proposal_version, proposal_item
