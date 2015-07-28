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
from adhocracy_core.workflows import transition_to_states


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
    parser.add_argument('--absolute',
                        help='use an absolute path for the list of states',
                        action='store_true')
    parser.add_argument('states',
                        type=str,
                        nargs='+',
                        help='list of state name to do transition to')
    parser.add_argument('--reset',
                        help='reset workflow to initial state',
                        action='store_true')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    _set_workflow_state(env['root'],
                        env['registry'],
                        args.resource_path,
                        args.states,
                        args.absolute,
                        args.reset,
                        )
    env['closer']()


def _get_states_to_transition(resource: IResource,
                              registry: Registry,
                              states: [str],
                              absolute,
                              reset) -> [str]:
    if not absolute or reset:
        return states
    workflow = registry.content.get_workflow(resource)
    state = workflow.state_of(resource)
    if state in states:
        return states[states.index(state) + 1:]
    return states


def _set_workflow_state(root: IResource,
                        registry: Registry,
                        resource_path: str,
                        states: [str],
                        absolute=False,
                        reset=False,
                        ):
    resource = find_resource(root, resource_path)
    states_to_transition = _get_states_to_transition(resource,
                                                     registry,
                                                     states,
                                                     absolute,
                                                     reset)
    if reset:
        transition_to_states(resource, states_to_transition, registry, reset=reset)
    else:
        transition_to_states(resource, states_to_transition, registry)
    transaction.commit()
