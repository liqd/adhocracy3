"""Script to set a workflow state for a given resource."""
import argparse
import inspect
import transaction

from pyramid.paster import bootstrap
from pyramid.registry import Registry
from pyramid.traversal import find_resource

from adhocracy_core.authorization import create_fake_god_request
from adhocracy_core.interfaces import IResource
from adhocracy_core.workflows import transition_to_states


def main():  # pragma: no cover
    """Set a workflow state for a given resource."""
    epilog = """
Below are some usages examples. We assume there is a process
associated to the ``/organisation/workshop`` resource with a standard
workflow.

To set a particular state, a relative path leading to the wanted state
is entered::

    ./bin/set_workflow_state etc/development.ini
    /organisation/workshop evaluate result closed

An absolute path can be given instead of a relative one with the
`absolute` option. The following command will put the workflow in the
'closed' state, whatever the current state is::

    ./bin/set_workflow_state --absolute etc/development.ini /organisation/workshop announce participate evaluate result closed

The current state and information about the workflow can be obtained
with the `info` option::

    ./bin/set_workflow_state --info etc/development.ini /organisation/workshop

The `reset` option is used to reset the workflow before setting the state::

    ./bin/set_workflow_state --reset etc/development.ini /organisation/workshop draft announce

    """  # noqa
    docstring = inspect.getdoc(main)
    parser = argparse.ArgumentParser(description=docstring,
                                     epilog=epilog,
                                     formatter_class=argparse
                                     .RawDescriptionHelpFormatter)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('resource_path',
                        type=str,
                        help='path of the resource')
    parser.add_argument('-i',
                        '--info',
                        help='display information about the workflow',
                        action='store_true')
    parser.add_argument('-a',
                        '--absolute',
                        help='use an absolute path for the list of states',
                        action='store_true')
    parser.add_argument('-r',
                        '--reset',
                        help='reset workflow before '
                        'transitioning to the states',
                        action='store_true')
    parser.add_argument('states',
                        type=str,
                        nargs='*',
                        help='list of state name to do transition to')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    if args.info:
        _print_workflow_info(env['root'],
                             env['registry'],
                             args.resource_path)
    else:
        set_workflow_state(env['root'],
                           env['registry'],
                           args.resource_path,
                           args.states,
                           args.absolute,
                           args.reset, )
    env['closer']()


def _print_workflow_info(root: IResource,
                         registry: Registry,
                         resource_path: str):
    resource = find_resource(root, resource_path)
    workflow = registry.content.get_workflow(resource)
    states = set(registry.content.workflows_meta[workflow.type]['states']
                 .keys())
    print('\nname: {}\ncurrent state: {}\nnext states: {}'
          '\nall states (unordered): {}\n'
          .format(workflow.type,
                  workflow.state_of(resource),
                  workflow.get_next_states(resource,
                                           create_fake_god_request(registry)),
                  states))


def _get_states_to_transition(resource: IResource,
                              registry: Registry,
                              states: [str],
                              absolute,
                              reset) -> [str]:
    _check_states(states)
    if not absolute or reset:
        return states
    workflow = registry.content.get_workflow(resource)
    state = workflow.state_of(resource)
    if state in states:
        return states[states.index(state) + 1:]
    return states


def _check_states(states):
    for state in states:
        if states.count(state) > 1:
            raise ValueError('Duplicate state: {}'.format(state))


def set_workflow_state(root: IResource,
                       registry: Registry,
                       resource_path: str,
                       states: [str],
                       absolute=False,
                       reset=False,
                       ):
    """Set a workflow state for a given resource."""
    resource = find_resource(root, resource_path)
    states_to_transition = _get_states_to_transition(resource,
                                                     registry,
                                                     states,
                                                     absolute,
                                                     reset)
    transition_to_states(resource,
                         states_to_transition,
                         registry,
                         reset=reset)
    transaction.commit()
