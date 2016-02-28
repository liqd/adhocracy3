"""adhocracy_core scripts."""

import logging
import json
import os


from pyramid.request import Request
from pyramid.registry import Registry
from pyramid.traversal import find_resource
from pyramid.traversal import resource_path
from pyrsistent import PMap
from pyrsistent import freeze
from pyrsistent import ny
from substanced.interfaces import IUserLocator
from zope.interface.interfaces import IInterface

from adhocracy_core.authorization import create_fake_god_request
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IPool
from adhocracy_core.schema import ContentType
from adhocracy_core.sheets.name import IName

logger = logging.getLogger(__name__)


def import_resources(root: IResource, registry: Registry, filename: str):
    """Import resources from a JSON file with dummy `god` user."""
    request = create_fake_god_request(registry)
    resources_info = _load_resources_info(filename)
    for resource_info in resources_info:
        expected_path = _get_expected_path(resource_info)
        if _resource_exists(expected_path, root):
            logger.info('Skipping {}.'.format(expected_path))
        else:
            logger.info('Creating {}'.format(expected_path))
            _create_resource(freeze(resource_info), request, registry, root)


def _get_expected_path(resource_info: dict) -> str:
    name_field = resource_info['data'].get(IName.__identifier__, {})
    name = name_field.get('name', '')
    path = name and os.path.join(resource_info['path'], name)
    return path


def _create_request(root: IPool, registry: Registry) -> Request:
    request = Request.blank('/')
    return request


def _resource_exists(expected_path: dict, context: IResource) -> bool:
    try:
        find_resource(context, expected_path)
        return True
    except KeyError:
        return False


def _create_resource(resource_info: PMap,
                     request: Request,
                     registry: Registry,
                     root: IPool):
    iresource = _deserialize_content_type(resource_info)
    parent = find_resource(root, resource_info['path'])
    resource_info = _resolve_users(resource_info, root, registry, request)
    appstructs = _deserialize_data(resource_info, parent, registry, request)
    creator = _get_creator(resource_info, root, registry, request)
    registry.content.create(iresource.__identifier__,
                            parent=parent,
                            appstructs=appstructs,
                            registry=registry,
                            request=request,
                            creator=creator,
                            )


def _load_resources_info(filename: str) -> [dict]:
    with open(filename, 'r') as f:
        return json.load(f)


def _resolve_users(resource_info: PMap,
                   root: IResource,
                   registry: Registry,
                   request: Request) -> PMap:
    """Resolve strings containing "user_by_name: <username>".

    Strings of this form are resolved to the user's path.

    """
    def _resolve_user(s):
        if not isinstance(s, str) or not s.startswith('user_by_login:'):
            return s
        user_locator = registry.getMultiAdapter((root, request),
                                                IUserLocator)
        user_name = s.split('user_by_login:')[1]
        user = user_locator.get_user_by_login(user_name)
        if user is None:
            raise ValueError('No such user: {}.'.format(user_name))
        return resource_path(user)

    return resource_info.transform(['data', ny, ny], _resolve_user)


def _deserialize_content_type(resource_info: dict) -> IInterface:
    schema = ContentType().bind(creating=True)
    iresource = schema.deserialize(resource_info['content_type'])
    return iresource


def _deserialize_data(resource_info: dict,
                      parent: IPool,
                      registry: Registry,
                      request: Request) -> dict:
    appstructs = {}
    iresource = _deserialize_content_type(resource_info)
    data = resource_info['data']
    sheets = registry.content.get_sheets_create(parent, iresource=iresource,
                                                request=request)
    for sheet in sheets:
        sheet_name = sheet.meta.isheet.__identifier__
        if sheet_name not in data:
            continue
        appstruct = sheet.deserialize(data[sheet_name])
        appstructs[sheet_name] = appstruct
    return appstructs


def _get_creator(resource_info: dict,
                 context: IResource,
                 registry: Registry,
                 request: Request) -> IResource:
    creator_name = resource_info.get('creator', None)
    if not creator_name:
        return None
    locator = registry.getMultiAdapter((context, request), IUserLocator)
    creator = locator.get_user_by_login(creator_name)
    return creator
