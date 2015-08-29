""" Adhocracy catalog extensions."""
from datetime import datetime
from substanced.catalog import Field
from pyramid.traversal import find_interface

from adhocracy_core.catalog.adhocracy import AdhocracyCatalogIndexes
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_s1.resources.s1 import IProcess
from adhocracy_s1.resources.s1 import IProposal


class S1CatalogIndexes(AdhocracyCatalogIndexes):

    """S1 indexes for the adhocracy catalog."""

    decision_date = Field()
    """Date when the decision was made which agenda s1 proposals
       will be discussed in the meeting.
    """


def index_decision_date_of_process(context, default) -> datetime:
    """Return value for `decision_date` index."""
    decision_date = _get_start_date_of_process_state_result(context)
    if decision_date is None:
        return default
    state = get_sheet_field(context, IWorkflowAssignment, 'workflow_state')
    if state in ('selected', 'rejected') and decision_date is not None:
        return decision_date
    else:
        return default


def _get_start_date_of_process_state_result(context) -> str:
    process = find_interface(context, IProcess)
    if process is None:
        return
    state_data = get_sheet_field(process, IWorkflowAssignment, 'state_data')
    result_state_data = [x for x in state_data if x['name'] == 'result']
    if result_state_data:
        start_date = result_state_data[0].get('start_date', None)
        return start_date


def includeme(config):
    """Register catalog utilities and index functions."""
    config.add_catalog_factory('adhocracy', S1CatalogIndexes)
    config.add_indexview(index_decision_date_of_process,
                         catalog_name='adhocracy',
                         index_name='decision_date',
                         context=IProposal,
                         )
