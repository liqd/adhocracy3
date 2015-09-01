""" Adhocracy catalog extensions."""
from datetime import datetime
from substanced.catalog import Field
from pyramid.traversal import find_interface

from adhocracy_core.catalog.adhocracy import AdhocracyCatalogIndexes
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_s1.resources.s1 import IProposal
from adhocracy_s1.resources.s1 import IProposalVersion


class S1CatalogIndexes(AdhocracyCatalogIndexes):

    """S1 indexes for the adhocracy catalog."""

    decision_date = Field()
    """Date when the decision was made which agenda s1 proposals
       will be discussed in the meeting.
    """


def index_decision_date(context, default) -> datetime:
    """Return value for `decision_date` index."""
    context = find_interface(context, IWorkflowAssignment)
    if context is None:
        return 'default'
    state_data = get_sheet_field(context, IWorkflowAssignment, 'state_data')
    datas = [x for x in state_data
             if x['name'] in ['result', 'selected', 'rejected']]
    if datas:
        decision_date = datas[0].get('start_date', default)
        return decision_date
    else:
        return default


def includeme(config):
    """Register catalog utilities and index functions."""
    config.add_catalog_factory('adhocracy', S1CatalogIndexes)
    config.add_indexview(index_decision_date,
                         catalog_name='adhocracy',
                         index_name='decision_date',
                         context=IProposalVersion,
                         )
    config.add_indexview(index_decision_date,
                         catalog_name='adhocracy',
                         index_name='decision_date',
                         context=IProposal,
                         )
