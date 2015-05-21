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
    resources_info = [_resolve_sheets_resources(info, context) for info in resources_info]
    resources_info = [_resolve_path(info, context) for info in resources_info]
    resources_info = [_deserialize_content_type(info, context) for info in resources_info]
    for resource_info in resources_info:
        _create_resource(resource_info, context, registry)
    transaction.commit()


def _create_resource(resource_info: dict, context: IResource, registry: Registry):
    registry.content.create(resource_info['content_type'].__identifier__,
                            parent=resource_info['path'],
                            appstructs=resource_info['data'],
                            after_creation=False,  # TODO: correct?
                            registry=registry)
    # TODO set creator


def _deserialize_content_type(resource_info: dict, context: IResource) -> dict:
    schema = ContentType()
    request = Request.blank('/')
    request.root = context
    resource_info['content_type'] = schema.bind(request=request) \
                                          .deserialize(resource_info['content_type'])
    return resource_info


def _resolve_path(resource_info: dict, context: IResource) -> dict:
    resource_info['path'] = find_resource(context, resource_info['path'])
    return resource_info


def _resolve_sheets_resources(resource_info: dict, context: IResource) -> dict:
    data = resource_info['data']
    for sheets_info in data.values():
        for k, v in sheets_info.items():
            if len(k) > 1 and v[0] == '/':
                sheets_info[k] = find_resource(context, v)
    return resource_info


def _load_resources_info(filename: str) -> [dict]:
    with open(filename, 'r') as f:
        return json.load(f)
