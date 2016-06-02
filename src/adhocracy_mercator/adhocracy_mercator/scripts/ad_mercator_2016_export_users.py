"""Script to export users and their proposal rates."""

import argparse
import inspect
from pyramid.paster import bootstrap

from .common import export_users_and_proposals_rates

from adhocracy_core.utils import create_filename
from adhocracy_mercator.resources.mercator2 import IMercatorProposal


def main():
    """Export all users and their proposal rates to csv file."""
    docstring = inspect.getdoc(main)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('min_rate',
                        type=int,
                        help='minimal rate to restrict listed proposals')
    parser.add_argument('-p',
                        '--include-passwords',
                        help='export passwords (in bcrypted form)',
                        action='store_true')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    filename = create_filename(directory='./var/export/',
                               prefix='adhocracy-users',
                               suffix='.csv')
    export_users_and_proposals_rates(env['root'], filename, IMercatorProposal,
                                     env['registry'], args)
    env['closer']()
