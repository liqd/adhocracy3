"""Script to automatically transition workflow states."""

import transaction
import argparse
import inspect
import logging

from datetime import datetime
from pyramid.paster import bootstrap
from pyramid.registry import Registry
from substanced.util import find_service
from substanced.interfaces import IRoot

from adhocracy_core.authorization import create_fake_god_request
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import search_query
from adhocracy_core.resources.process import IProcess
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.workflows import transition_to_states
from adhocracy_core.utils import now


logger = logging.getLogger(__name__)


def main():  # pragma: no cover
    """Automatically transition workflow states of processes.

    The transition is decided based on the start_date value im the state_data
    of the workflow-assignment and the auto_transition setting of the
    workflow.
    """
    docstring = inspect.getdoc(main)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    auto_transition_process_workflow(env['root'], env['registry'])
    transaction.commit()
    env['closer']()


def auto_transition_process_workflow(root: IRoot, registry: Registry):
    """Automatically transition workflow states of processes."""
    date_now = now()
    processes = _get_processes_with_auto_transition(root, registry)
    for process in processes:
        is_outdated = _state_is_outdated(process, registry, date_now)
        if is_outdated:
            _do_auto_transition(process, registry)


def _get_processes_with_auto_transition(root: IRoot,
                                        registry: Registry) -> [IResource]:
    catalogs = find_service(root, 'catalogs')
    query = search_query._replace(interfaces=IProcess)
    processes = catalogs.search(query).elements
    processes_with_auto_transition = filter(
        lambda r: _auto_transition_enabled(r, registry),
        processes)
    return processes_with_auto_transition


def _auto_transition_enabled(context: IResource, registry: Registry):
    workflow_assignment = registry.content.get_sheet(context,
                                                     IWorkflowAssignment)
    workflow_name = workflow_assignment.get()['workflow']
    workflow_meta = registry.content.workflows_meta[workflow_name]
    return workflow_meta['auto_transition']


def _state_is_outdated(context: IResource, registry: Registry,
                       date_now: datetime) -> bool:
    workflow = registry.content.get_workflow(context)
    next_states = workflow.get_next_states(context,
                                           create_fake_god_request(registry))
    if len(next_states) == 1:
        next_state = next_states[0]
        start_date_next = _get_next_state_start_date(context, registry,
                                                     next_state)
        if start_date_next:
            return date_now > start_date_next
    return False


def _get_next_state_start_date(context: IResource, registry: Registry,
                               next_state: str) -> datetime:
    workflow_assignment = registry.content.get_sheet(context,
                                                     IWorkflowAssignment)
    state_data_list = workflow_assignment.get()['state_data']
    for state_data in state_data_list:
        if state_data['name'] == next_state:
            next_state_data = state_data
            return next_state_data['start_date']
    return None


def _do_auto_transition(context: IResource, registry: Registry):
    workflow = registry.content.get_workflow(context)
    next_states = workflow.get_next_states(context,
                                           create_fake_god_request(registry))
    print('Auto-transition of {} workflow to state {}.'
          .format(context, next_states))
    transition_to_states(context, next_states, registry)
