"""Agenda s1 workflow."""

from datetime import datetime
from pytz import UTC
from pyramid.request import Request
from substanced.util import find_service
from adhocracy_core.exceptions import RuntimeConfigurationError
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import search_query
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.utils import get_sheet


def do_transition_to_propose(context: IPool, request: Request, **kwargs):
    """Do various tasks to complete transition to propose state."""
    _remove_state_data(context, 'result', 'start_date', request)


def do_transition_to_voteable(context: IPool, request: Request, **kwargs):
    """Do transition from state proposed to voteable for all children."""
    for child in context.values():
        _do_transition(child, request, from_state='proposed',
                       to_state='voteable')


def do_transition_to_result(context: IPool, request: Request, **kwargs):
    """Do various tasks to complete transition to result state."""
    decision_date = datetime.utcnow().replace(tzinfo=UTC)
    _store_state_data(context, 'result', request, start_date=decision_date)
    _change_children_to_rejected_or_selected(context, request,
                                             start_date=decision_date)


def _change_children_to_rejected_or_selected(context: IPool, request: Request,
                                             start_date: datetime=None):
    """Do transition from state proposed to rejected/selected for all children.

    The most rated child does transition to state selected, the other to
    rejected.
    Save decision_date in state assignment data.
    """
    rated_children = _get_children_sort_by_rates(context)
    for pos, child in enumerate(rated_children):
        if pos == 0:
            _do_transition(child, request, from_state='voteable',
                           to_state='selected', start_date=start_date)
        else:
            _do_transition(child, request, from_state='voteable',
                           to_state='rejected', start_date=start_date)


def _store_state_data(context: IWorkflowAssignment, state_name: str,
                      request: Request, **kwargs):
    sheet = get_sheet(context, IWorkflowAssignment)
    state_data = sheet.get()['state_data']
    datas = [x for x in state_data if x['name'] == state_name]
    if datas == []:
        data = {'name': state_name}
        state_data.append(data)
    else:
        data = datas[0]
    data.update(**kwargs)
    sheet.set({'state_data': state_data}, request=request)


def _remove_state_data(context: IWorkflowAssignment, state_name: str,
                       key: str, request: Request):
    sheet = get_sheet(context, IWorkflowAssignment)
    state_data = sheet.get()['state_data']
    datas = [x for x in state_data if x['name'] == state_name]
    if datas == []:
        return
    data = datas[0]
    if key in data:
        del data[key]
    sheet.set({'state_data': state_data}, request=request)


def _get_children_sort_by_rates(context) -> []:
    catalog = find_service(context, 'catalogs')
    if catalog is None:
        return []  # ease testing
    result = catalog.search(search_query._replace(root=context,
                                                  depth=2,
                                                  only_visible=True,
                                                  interfaces=(IRateable,
                                                              IVersionable),
                                                  sort_by='rates',
                                                  reverse=True,
                                                  indexes={'tag': 'LAST',
                                                           'workflow_state':
                                                               'voteable'},

                                                  ))
    return (r.__parent__ for r in result.elements)


def _do_transition(context, request: Request, from_state: str, to_state: str,
                   start_date: datetime=None):
    try:
        sheet = request.registry.content.get_sheet(context,
                                                   IWorkflowAssignment)
    except RuntimeConfigurationError:
        pass
    else:
        current_state = sheet.get()['workflow_state']
        if current_state == from_state:
            sheet.set({'workflow_state': to_state}, request=request)
            if start_date is not None:
                _store_state_data(context, to_state, request,
                                  start_date=start_date)


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_s1.workflows:s1.yaml', 's1')
    config.add_workflow('adhocracy_s1.workflows:s1_content.yaml', 's1_content')
