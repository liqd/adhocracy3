"""Import/create resources into the system.

This is registered as console script 'import_resources' in setup.py.

"""
# pragma: no cover

import argparse
import inspect
import logging
import sys
import transaction

from pyramid.paster import bootstrap

from adhocracy_core import scripts


def import_resources():
    """Import resources from a JSON file.

    usage::

        bin/import_resources etc/development.ini  <filename>
    """
    epilog = """The input JSON file contains the interface name of the resource
    type to create and a serialization of the sheets data.

    Strings having the form 'user_by_login: <username>' are resolved
    to the user's path.

    """
    docstring = inspect.getdoc(import_resources)
    parser = argparse.ArgumentParser(description=docstring, epilog=epilog)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('filename',
                        type=str,
                        help='file containing the resources descriptions')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    scripts.import_resources(env['root'], env['registry'], args.filename)
    transaction.commit()
    env['closer']()
