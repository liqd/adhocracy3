"""Import/create users into the system.

This is registered as console script 'import_users' in setup.py.

"""
import argparse
import inspect
import json

import adhocracy_core.sheets.principal
import transaction
from adhocracy_core.interfaces import IResource
from adhocracy_core.resources.principal import IUser
from adhocracy_core.sheets.principal import IPermissions
from pyramid.paster import bootstrap
from pyramid.registry import Registry
from pyramid.request import Request
from substanced.interfaces import IUserLocator
from substanced.util import find_service
from adhocracy_core.utils import get_sheet
from adhocracy_core.sheets.principal import IPasswordAuthentication
from adhocracy_core.sheets.principal import IUserExtended


def import_users():
    """Import users from a JSON file.

    Already existing users will have their groups, roles and emails updated.

    usage::

        bin/import_users etc/development.ini  <filename>
    """
    docstring = inspect.getdoc(import_users)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('filename',
                        type=str,
                        help='file containing the users')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    _import_users(env['root'], env['registry'], args.filename)
    env['closer']()


def _import_users(context: IResource, registry: Registry, filename: str):
    registry.settings['adhocracy.skip_registration_mail'] = True
    users_info = _load_users_info(filename)
    users = find_service(context, 'principals', 'users')
    groups = find_service(context, 'principals', 'groups')
    locator = _get_user_locator(context, registry)
    for user_info in users_info:
        user = locator.get_user_by_login(user_info['name'])
        if user:
            print('Updating user {}'.format(user.name))
            _update_user(user, user_info, groups)
        else:
            print('Creating user {}'.format(user_info['name']))
            _create_user(user_info, users, registry, groups)
    transaction.commit()
    # TODO update some catalogs?


def _load_users_info(filename: str) -> [dict]:
    with open(filename, 'r') as f:
        return json.load(f)


def _update_user(user: IUser, user_info: dict, groups: IResource):
    userextended_sheet = get_sheet(user, IUserExtended)
    userextended_sheet.set({'email': user_info['email']})
    user_groups = _get_groups(user_info['groups'], groups)
    permissions_sheet = get_sheet(user, IPermissions)
    permissions_sheet.set({'roles': user_info['roles'],
                           'groups': user_groups})
    password_sheet = get_sheet(user, IPasswordAuthentication)
    password_sheet.set({'password': user_info['password']})


def _get_groups(groups_names: [str], groups: IResource) -> [IResource]:
    """Map groups names to their instances."""
    return [groups[name] for name in groups_names]


def _create_user(user_info: dict, users: IResource, registry: Registry,
                 groups: IResource):
    groups = _get_groups(user_info['groups'], groups)
    appstruct = {adhocracy_core.sheets.principal.IUserBasic.__identifier__:
                 {'name': user_info['name']},
                 adhocracy_core.sheets.principal.IUserExtended.__identifier__:
                 {'email': user_info['email']},
                 adhocracy_core.sheets.principal.IPermissions.__identifier__:
                 {'roles': user_info['roles'], 'groups': groups},
                 adhocracy_core.sheets.principal.IPasswordAuthentication.
                 __identifier__: {'password': user_info['password']},
                 }
    user = registry.content.create(IUser.__identifier__,
                                   users,
                                   appstruct,
                                   registry=registry)
    user.activate()


def _get_user_locator(context: IResource, registry: Registry) -> IUserLocator:
    request = Request.blank('/dummy')
    locator = registry.getMultiAdapter((context, request), IUserLocator)
    return locator
