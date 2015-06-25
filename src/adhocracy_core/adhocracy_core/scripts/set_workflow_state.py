"""Set a workflow state for a given resource.

This is registered as console script in setup.py.
"""
import argparse
import inspect
import transaction

from pyramid.paster import bootstrap
from pyramid.registry import Registry
from pyramid.traversal import find_resource

from adhocracy_core.interfaces import IResource
from adhocracy_core.workflows import setup_workflow
from adhocracy_core.workflows import get_workflow


def set_workflow_state():  # pragma: no cover
    """Set a workflow state for a given resource.

    usage::

        bin/set_workflow_state etc/development.ini <resource-path> <state>
    """
    docstring = inspect.getdoc(set_workflow_state)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('resource_path',
                        type=str,
                        help='path of the resource')
    parser.add_argument('state',
                        type=str,
                        help='name of the state')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    _set_workflow_state(env['root'],
                        env['registry'],
                        args.resource_path,
                        args.workflow_name,
                        args.state)
    env['closer']()


def _set_workflow_state(root: IResource,
                        registry: Registry,
                        resource_path: str,
                        state: str):
    resource = find_resource(root, resource_path)
    workflow = get_workflow(resource, registry)
    states = registry.content.workflows_meta[workflow.type]['states_order']
    to_transition = states[1:states.index(state) + 1]
    setup_workflow(resource, to_transition, registry)
    transaction.commit()
