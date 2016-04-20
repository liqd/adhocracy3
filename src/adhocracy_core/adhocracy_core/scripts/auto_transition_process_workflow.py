"""Automatically transition workflow states.

This is registered as console script.
"""
import transaction
import argparse
import inspect
import logging

from pyramid.paster import bootstrap
from pyramid.registry import Registry
from substanced.util import find_service

from adhocracy_core.authorization import create_fake_god_request
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import search_query
from adhocracy_core.resources.process import IProcess
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.workflows import transition_to_states
from adhocracy_core.utils import now


logger = logging.getLogger(__name__)


def auto_transition_process_workflow():  # pragma: no cover
    """Automatically transition workflow states.

    usage::

        bin/auto_auto_transition_process_workflow etc/development.ini
    """
    docstring = inspect.getdoc(auto_transition_process_workflow)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    _auto_transition_process_workflow(env['root'], env['registry'])
    transaction.commit()
    env['closer']()


def _auto_transition_process_workflow(context: IResource, registry: Registry):
    catalogs = find_service(context, 'catalogs')
    query = search_query._replace(interfaces=IProcess,
                                  resolve=True
                                  )
    processes = catalogs.search(query).elements
    for process in processes:
        workflow_assignment = registry.content.get_sheet(process,
                                                         IWorkflowAssignment)
        if _workflow_auto_transition_enabled(registry, workflow_assignment) \
            and _workflow_auto_transition_needed(process, registry,
                                                 workflow_assignment):
            _do_workflow_auto_transition(process, registry)


def _workflow_auto_transition_enabled(
        registry: Registry, workflow_assignment: IWorkflowAssignment):
    workflow_name = workflow_assignment.get()['workflow']
    workflow_meta = registry.content.workflows_meta[workflow_name]
    return workflow_meta['auto_transition']


def _workflow_auto_transition_needed(context: IResource, registry: Registry,
                                     workflow_assignment: IWorkflowAssignment):
    workflow = registry.content.get_workflow(context)
    next_states = workflow.get_next_states(context,
                                           create_fake_god_request(registry))
    if len(next_states) == 1:
        next_state = next_states[0]
        end_date = _get_current_state_end_date(workflow_assignment, next_state)
        if end_date:
            return now() > end_date
    return False


def _get_current_state_end_date(workflow_assignment: IWorkflowAssignment,
                                next_state: str):
    current_state = workflow_assignment.get()['workflow_state']
    state_data_list = workflow_assignment.get()['state_data']
    current_state_data = None
    next_state_data = None
    for state_data in state_data_list:
        if state_data['name'] == current_state:
            current_state_data = state_data
        if state_data['name'] == next_state:
            next_state_data = state_data
    if current_state_data:
        if next_state_data and \
                current_state_data['end_date'] != \
                next_state_data['start_date']:
            print('Conflicting workflow assignment: {}.'
                  .format(workflow_assignment))
            return None
        return current_state_data['end_date']
    if next_state_data:
        return next_state_data['start_date']
    return None


def _do_workflow_auto_transition(context: IResource, registry: Registry):
    workflow = registry.content.get_workflow(context)
    next_states = workflow.get_next_states(context,
                                           create_fake_god_request(registry))
    print('Auto-transition of {} workflow to state {}.'
          .format(context, next_states))
    transition_to_states(context, next_states, registry)
