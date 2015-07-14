"""Import local roles resources into the system.

This is registered as console script 'bin/import_local_roles.py' in setup.py.

"""
import argparse
import inspect
import json
import transaction

from pyramid.paster import bootstrap
from adhocracy_core.interfaces import IResource
from pyramid.registry import Registry
from adhocracy_core.authorization import set_local_roles
from pyramid.traversal import find_resource


def import_local_roles():  # pragma: no cover
    """Import/set local roles from a JSON file.

    usage::

        bin/import_local_roles etc/development.ini  <filename>
    """
    docstring = inspect.getdoc(import_local_roles)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('filename',
                        type=str,
                        help='file containing the resources descriptions')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    _import_local_roles(env['root'], env['registry'], args.filename)
    env['closer']()


def _import_local_roles(context: IResource, registry: Registry, filename: str):
    multi_local_roles_info = _load_local_roles_info(filename)
    for local_roles_info in multi_local_roles_info:
        _set_local_roles(local_roles_info, context, registry)
    transaction.commit()


def _set_local_roles(local_roles_info: dict, context: IResource,
                     registry: Registry):
    resource = find_resource(context, local_roles_info['path'])
    local_roles_info['roles'] = _deserialize_roles(local_roles_info['roles'])
    set_local_roles(resource, local_roles_info['roles'])


def _deserialize_roles(roles: dict) -> dict:
    for k, v in roles.items():
        roles[k] = set(v)
    return roles


def _load_local_roles_info(filename: str) -> [dict]:
    with open(filename, 'r') as f:
        return json.load(f)
