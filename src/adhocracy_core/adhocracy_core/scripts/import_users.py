"""Import/create users into the system.

This is registered as console script 'import_users' in setup.py.

"""
import argparse
import inspect
import json

import transaction
from pyramid.paster import bootstrap
from pyramid.registry import Registry
from pyramid.request import Request
from substanced.interfaces import IUserLocator
from substanced.util import find_service

from adhocracy_core.interfaces import IResource
from adhocracy_core.resources.principal import IUser
from adhocracy_core.resources.principal import IPasswordReset
from adhocracy_core.resources.badge import IBadge
from adhocracy_core.utils import get_sheet
from adhocracy_core import sheets
from adhocracy_core.scripts.assign_badges import create_badge_assignment


def import_users():  # pragma: no cover
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
            send_invitation = user_info.get('send_invitation_mail', False)
            activate = not send_invitation
            user = _create_user(user_info, users, registry, groups,
                                activate=activate)
            if send_invitation:
                print('Sending invitation mail to user {}'.format(user.name))
                _send_invitation_mail(user, user_info, registry)
            badge_names = user_info.get('badges', [])
            if badge_names:
                print('Assign badge for user {}'.format(user.name))
                badges = _create_badges(user, badge_names, registry)
                _assign_badges(user, badges, registry)
    transaction.commit()


def _load_users_info(filename: str) -> [dict]:
    with open(filename, 'r') as f:
        return json.load(f)


def _update_user(user: IUser, user_info: dict, groups: IResource):
    userextended_sheet = get_sheet(user, sheets.principal.IUserExtended)
    userextended_sheet.set({'email': user_info['email']})
    user_groups = _get_groups(user_info['groups'], groups)
    permissions_sheet = get_sheet(user, sheets.principal.IPermissions)
    permissions_sheet.set({'roles': user_info['roles'],
                           'groups': user_groups})


def _get_groups(groups_names: [str], groups: IResource) -> [IResource]:
    """Map groups names to their instances."""
    return [groups[name] for name in groups_names]


def _create_user(user_info: dict, users: IResource, registry: Registry,
                 groups: IResource, activate=True) -> IUser:
    groups = _get_groups(user_info['groups'], groups)
    appstruct = {sheets.principal.IUserBasic.__identifier__:
                 {'name': user_info['name']},
                 sheets.principal.IUserExtended.__identifier__:
                 {'email': user_info['email']},
                 sheets.principal.IPermissions.__identifier__:
                 {'roles': user_info['roles'], 'groups': groups},
                 sheets.principal.IPasswordAuthentication.
                 __identifier__: {'password': user_info['initial-password']},
                 }
    user = registry.content.create(IUser.__identifier__,
                                   users,
                                   appstruct,
                                   registry=registry,
                                   send_event=False)
    if activate:
        user.activate()
    return user


def _send_invitation_mail(user: IUser, user_info: dict, registry: Registry):
    resets = find_service(user, 'principals', 'resets')
    reset = registry.content.create(IPasswordReset.__identifier__,
                                    parent=resets,
                                    creator=user,
                                    send_event=False,
                                    )
    subject_tmpl = user_info.get('subject_tmpl_invitation_mail', None)
    body_tmpl = user_info.get('body_tmpl_invitation_mail', None)
    registry.messenger.send_invitation_mail(user, reset,
                                            subject_tmpl=subject_tmpl,
                                            body_tmpl=body_tmpl,
                                            )
    return user


def _get_user_locator(context: IResource, registry: Registry) -> IUserLocator:
    request = Request.blank('/dummy')
    locator = registry.getMultiAdapter((context, request), IUserLocator)
    return locator


def _create_badges(user: IUser, badge_names: [str],
                   registry: Registry) -> [IBadge]:
    badges_service = find_service(user, 'badges')
    badges = []
    for name in badge_names:
        badge = badges_service.get(name, None)
        if badge is None:
            appstructs = {sheets.name.IName.__identifier__: {'name': name}}
            badge = registry.content.create(IBadge.__identifier__,
                                            parent=badges_service,
                                            appstructs=appstructs)
        badges.append(badge)
    return badges


def _assign_badges(user: IUser, badges: [IBadge], registry: Registry):
    for badge in badges:
        create_badge_assignment(user, badge, user, '', registry)
