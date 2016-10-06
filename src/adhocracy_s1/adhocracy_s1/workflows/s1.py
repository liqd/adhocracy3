"""Agenda s1 workflow."""

from datetime import datetime
from pytz import UTC
from pyramid.request import Request
from pyramid.registry import Registry
from substanced.util import find_service
from adhocracy_core.catalog.adhocracy import index_rates
from adhocracy_core.exceptions import RuntimeConfigurationError
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import search_query
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.resources.proposal import IProposal
from adhocracy_core.resources.proposal import IProposalVersion
from adhocracy_core.sheets.description import IDescription
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.tags import ITags


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
                      request: Request,
                      **kwargs):
    sheet = request.registry.content.get_sheet(context,
                                               IWorkflowAssignment,
                                               request=request)
    state_data = sheet.get()['state_data']
    datas = [x for x in state_data if x['name'] == state_name]
    if datas == []:
        data = {'name': state_name}
        state_data.append(data)
    else:
        data = datas[0]
    data.update(**kwargs)
    sheet.set({'state_data': state_data})


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
                                                   IWorkflowAssignment,
                                                   request=request)
    except RuntimeConfigurationError:
        pass  # we ignore context without IWorklowAssignment sheet
    else:
        current_state = sheet.get()['workflow_state']
        if current_state == from_state:
            sheet.set({'workflow_state': to_state})
            if start_date is not None:
                _store_state_data(context, to_state, request,
                                  start_date=start_date)


def do_transition_to_proposed(context: IProposal,
                              request: Request,
                              **kwargs) -> None:
    """Delete rates for `context` and add renominate info."""
    rates = find_service(context, 'rates')
    if rates is None:
        return
    last = request.registry.content.get_sheet_field(context, ITags, 'LAST')
    _add_renominate_info(last, request)
    _remove_children(rates, request.registry)


def _add_renominate_info(version: IProposalVersion, request: Request) -> None:
    registry = request.registry
    editor = registry.content.get_sheet_field(request.user, IUserBasic, 'name')
    rates = index_rates(version, 0)
    description_sheet = registry.content.get_sheet(version, IDescription)
    description = description_sheet.get()['description']
    renominate_info = '\n\n---'\
                      '\n\nErneut vorgeschlagen von: {0}'\
                      '\nBefürworter*innen davor: {1}'\
                      '\n'.format(editor, rates)
    description_sheet.set({'description': description + renominate_info})


def _remove_children(context: IPool, registry: Registry) -> None:
    child_names = [x for x in context.keys()]
    for child in child_names:
        context.remove(child, registry=registry)


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_s1.workflows:s1.yaml', 's1')
    config.add_workflow('adhocracy_s1.workflows:s1_content.yaml', 's1_content')
    config.add_workflow('adhocracy_s1.workflows:s1_private.yaml', 's1_private')
