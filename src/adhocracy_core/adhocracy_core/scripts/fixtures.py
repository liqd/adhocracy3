"""Import fixtures."""
import argparse
import logging
import sys
import transaction

from pyramid.paster import bootstrap

from adhocracy_core.interfaces import IFixtureAsset
from . import import_fixture


logger = logging.getLogger(__name__)


def import_fixtures():  # pragma: no cover
    args = _argparse()
    env = bootstrap(args.ini_file)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    _import_fixtures(env['root'],
                     env['registry'],
                     all=args.import_all,
                     custom=args.import_custom,
                     )
    env['closer']()


def _argparse():
    parser = argparse.ArgumentParser(description='Import adhocracy fixtures.')
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file',
                        default='etc/development.ini',
                        nargs='?')
    parser.add_argument('-a',
                        '--import_all',
                        help='Import all registered fixture directories.',
                        action='store_true')
    parser.add_argument('-c',
                        '--import_custom',
                        help='Import custom fixture name or file system path')
    return parser.parse_args()


def _import_fixtures(root,
                     registry,
                     all=False,
                     custom='',
                     ):
    assets = [x[0] for x in registry.getUtilitiesFor(IFixtureAsset)]
    log_only = False
    if custom:
        print('\nImport custom fixture:\n')
        assets = [custom]
    elif all:
        print('\nImport all fixtures:\n')
    else:
        print('\nThe following fixture directories are registered:')
        log_only = True
    for asset in assets:
        print('\nFixture {}'.format(asset))
        import_fixture(asset, root, registry, log_only=log_only)

