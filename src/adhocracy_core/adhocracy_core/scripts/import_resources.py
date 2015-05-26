"""Import/create resources into the system.

This is registered as console script 'import_resources' in setup.py.

"""
import argparse
import inspect
import json
import transaction

from pyramid.paster import bootstrap
from pyramid.request import Request
from adhocracy_core.interfaces import IResource
from pyramid.registry import Registry
from pyramid.traversal import find_resource
from adhocracy_core.schema import ContentType
from substanced.interfaces import IUserLocator


def import_resources():
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
    _import_resources(env['root'], env['registry'], args.filename)
    env['closer']()


def _import_resources(context: IResource, registry: Registry, filename: str):
    resources_info = _load_resources_info(filename)
    for resource_info in resources_info:
        resource_info = _resolve_sheets_resources(resource_info, context)
        resource_info = _resolve_path(resource_info, context)
        resource_info = _deserialize_content_type(resource_info, context)
        expected_path = _expected_path(resource_info)
        if _resource_exists(resource_info, context):
            print('Skipping {}.'.format(expected_path))
        else:
            print('Creating {}'.format(expected_path))
            _create_resource(resource_info, context, registry)
    transaction.commit()


def _resource_exists(resource_info: dict, context: IResource) -> bool:
    try:
        find_resource(context, _expected_path(resource_info))
        return True
    except KeyError:
        return False


def _expected_path(resource_info: dict) -> str:
    name = _get_resource_info_name(resource_info)
    if resource_info['path'] == '/':
        return '/' + name
    else:
        return resource_info['path'] + '/' + name


def _get_resource_info_name(resource_info: dict) -> str:
    name_field = resource_info['data'].get('adhocracy_core.sheets.name.IName', None)
    if name_field is None:
        return None
    name = name_field.get('name', None)
    return name


def _create_resource(resource_info: dict, context: IResource, registry: Registry):
    creator = _get_creator(resource_info, context, registry)
    registry.content.create(resource_info['content_type'].__identifier__,
                            parent=resource_info['parent'],
                            appstructs=resource_info['data'],
                            registry=registry,
                            creator=creator)


def _get_creator(resource_info: dict,
                 context: IResource,
                 registry: Registry) -> IResource:
    creator_name = resource_info.get('creator', None)
    if not creator_name:
        return None
    locator = _get_user_locator(context, registry)
    creator = locator.get_user_by_login(creator_name)
    return creator


def _deserialize_content_type(resource_info: dict, context: IResource) -> dict:
    schema = ContentType()
    request = Request.blank('/')
    request.root = context
    resource_info['content_type'] = schema.bind(request=request) \
                                          .deserialize(resource_info['content_type'])
    return resource_info


def _resolve_path(resource_info: dict, context: IResource) -> dict:
    resource_info['parent'] = find_resource(context, resource_info['path'])
    return resource_info


def _resolve_sheets_resources(resource_info: dict, context: IResource) -> dict:
    resource_info['data'] = _resolve_value(resource_info['data'], context)
    return resource_info


def _resolve_value(value, context):
    typ = type(value)
    if typ == list:
        return [_resolve_value(v, context) for v in value]
    elif typ == dict:
        for k, v in value.items():
            value[k] = _resolve_value(v, context)
        return value
    elif typ == str and len(value) > 1 and value[0] == '/':
        # assume path to a resource
        return find_resource(context, value)
    else:
        return value


def _load_resources_info(filename: str) -> [dict]:
    with open(filename, 'r') as f:
        return json.load(f)


def _get_user_locator(context: IResource, registry: Registry) -> IUserLocator:
    request = Request.blank('/dummy')
    locator = registry.getMultiAdapter((context, request), IUserLocator)
    return locator
