"""Import/create resources into the system.

This is registered as console script 'import_resources' in setup.py.

"""
import argparse
import inspect
import logging
import json
import os
import sys
import transaction

from pyramid.paster import bootstrap
from pyramid.request import Request
from pyramid.registry import Registry
from pyramid.traversal import find_resource
from substanced.interfaces import IUserLocator
from zope.interface.interfaces import IInterface

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IPool
from adhocracy_core.schema import ContentType
from adhocracy_core.sheets.name import IName


logger = logging.getLogger(__name__)


def import_resources():  # pragma: no cover
    """Import resources from a JSON file.

    usage::

        bin/import_resources etc/development.ini  <filename>
    """
    docstring = inspect.getdoc(import_resources)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('filename',
                        type=str,
                        help='file containing the resources descriptions')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    _import_resources(env['root'], env['registry'], args.filename)
    env['closer']()


def _import_resources(root: IResource, registry: Registry, filename: str):
    resources_info = _load_resources_info(filename)
    request = _create_request(root, registry)
    for resource_info in resources_info:
        expected_path = _get_expected_path(resource_info)
        if _resource_exists(expected_path, root):
            logger.info('Skipping {}.'.format(expected_path))
        else:
            logger.info('Creating {}'.format(expected_path))
            _create_resource(resource_info, request, registry, root)

    transaction.commit()


def _create_request(root: IPool, registry: Registry) -> Request:
    request = Request.blank('/')
    request.registry = registry
    request.root = root
    return request


def _get_expected_path(resource_info: dict) -> str:
    name_field = resource_info['data'].get(IName.__identifier__, {})
    name = name_field.get('name', '')
    path = name and os.path.join(resource_info['path'], name)
    return path


def _resource_exists(expected_path: dict, context: IResource) -> bool:
    try:
        find_resource(context, expected_path)
        return True
    except KeyError:
        return False


def _create_resource(resource_info: dict,
                     request: Request,
                     registry: Registry,
                     root: IPool):
    iresource = _deserialize_content_type(resource_info, request)
    parent = find_resource(root, resource_info['path'])
    appstructs = _deserialize_data(resource_info, parent, request, registry)
    creator = _get_creator(resource_info, root, registry)
    registry.content.create(iresource.__identifier__,
                            parent=parent,
                            appstructs=appstructs,
                            registry=request.registry,
                            request=request,
                            creator=creator,
                            )


def _deserialize_content_type(resource_info: dict,
                              request: Request) -> IInterface:
    schema = ContentType().bind(request=request)
    iresource = schema.deserialize(resource_info['content_type'])
    return iresource


def _deserialize_data(resource_info: dict, parent: IPool, request: Request,
                      registry: Registry) -> dict:
    appstructs = {}
    iresource = _deserialize_content_type(resource_info, request)
    data = resource_info['data']
    sheets = registry.content.get_sheets_create(parent, iresource=iresource)
    for sheet in sheets:
        sheet_name = sheet.meta.isheet.__identifier__
        if sheet_name not in data:
            continue
        schema = sheet.schema.bind(registry=registry,
                                   request=request,
                                   context=parent,
                                   parent_pool=parent)
        appstruct = schema.deserialize(data[sheet_name])
        appstructs[sheet_name] = appstruct
    return appstructs


def _get_creator(resource_info: dict,
                 context: IResource,
                 registry: Registry) -> IResource:
    creator_name = resource_info.get('creator', None)
    if not creator_name:
        return None
    locator = _get_user_locator(context, registry)
    creator = locator.get_user_by_login(creator_name)
    return creator


def _get_user_locator(context: IResource, registry: Registry) -> IUserLocator:
    request = Request.blank('/dummy')
    locator = registry.getMultiAdapter((context, request), IUserLocator)
    return locator


def _load_resources_info(filename: str) -> [dict]:
    with open(filename, 'r') as f:
        return json.load(f)
