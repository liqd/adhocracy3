from copy import deepcopy
from pyramid import testing
from pytest import fixture
from pytest import mark


def test_create_s1_catalog_indexes():
    from substanced.catalog import Field
    from .adhocracy import S1CatalogIndexes
    inst = S1CatalogIndexes()
    assert isinstance(inst.decision_date, Field)


class TestIndexDescisionDate:

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    @fixture
    def item(self):
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        item = testing.DummyResource(__provides__=IWorkflowAssignment)
        item['version'] = testing.DummyResource()
        return item

    def call_fut(self, *args):
        from .adhocracy import index_decision_date
        return index_decision_date(*args)

    def test_ignore_if_not_state_data_in_linegae(self, context, registry):
        assert self.call_fut(context, 'default') == 'default'

    def test_return_state_data_of_state_date_selected_in_lineage(
            self, item, registry, mock_sheet):
        from datetime import datetime
        decision_date = datetime.now()
        registry.content.get_sheet.return_value = mock_sheet
        mock_sheet.get.return_value = {'state_data': [{'name': 'selected',
                                                       'start_date': decision_date}]}
        assert self.call_fut(item['version'], 'default') == decision_date

    def test_return_state_data_of_state_date_rejected_in_lineage(
            self, item, registry, mock_sheet):
        from datetime import datetime
        decision_date = datetime.now()
        registry.content.get_sheet.return_value = mock_sheet
        mock_sheet.get.return_value = {'state_data': [{'name': 'rejected',
                                                       'start_date': decision_date}]}
        assert self.call_fut(item['version'], 'default') == decision_date


    @mark.usefixtures('integration')
    def test_register(self, registry):
        from adhocracy_s1.resources.s1 import IProposal
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((IProposal,), IIndexView,
                                        name='adhocracy|decision_date')

    @mark.usefixtures('integration')
    def test_register(self, registry):
        from adhocracy_s1.resources.s1 import IProposalVersion
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((IProposalVersion,), IIndexView,
                                        name='adhocracy|decision_date')


@mark.usefixtures('integration')
def test_create_adhocracy_catalog(pool_graph, registry):
    from substanced.catalog import Catalog
    context = pool_graph
    catalogs = registry.content.create('Catalogs')
    context.add_service('catalogs', catalogs, registry=registry)
    catalogs.add_catalog('adhocracy')

    assert isinstance(catalogs['adhocracy'], Catalog)
    # default indexes
    assert 'tag' in catalogs['adhocracy']
    # s1 indexes
    assert 'decision_date' in catalogs['adhocracy']
