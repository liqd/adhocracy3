from copy import deepcopy
from pyramid import testing
from pytest import fixture
from pytest import mark


def test_create_s1_catalog_indexes():
    from substanced.catalog import Field
    from .adhocracy import S1CatalogIndexes
    inst = S1CatalogIndexes()
    assert isinstance(inst.decision_date, Field)


class TestIndexDescisionDateOfProcess:

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    @fixture
    def process(self, item):
        from adhocracy_s1.resources.s1 import IProcess
        process = testing.DummyResource(__provides__=IProcess)
        process['item'] = item
        return process

    @fixture
    def process_workflow_sheet(self, mock_sheet):
        return deepcopy(mock_sheet)

    @fixture
    def item_workflow_sheet(self, mock_sheet):
        return deepcopy(mock_sheet)

    def call_fut(self, *args):
        from .adhocracy import index_decision_date_of_process
        return index_decision_date_of_process(*args)

    def test_return_default_if_no_process_in_lineage(self, item):
        item.__parent__ = None
        assert self.call_fut(item, 'default') == 'default'

    def test_return_default_if_process_has_no_result_start_date(
            self, item, process, process_workflow_sheet, registry):
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        registry.content.get_sheet.return_value = process_workflow_sheet
        process_workflow_sheet.get.return_value = {'state_data': []}
        assert self.call_fut(item, 'default') == 'default'
        registry.content.get_sheet.assert_called_with(process, IWorkflowAssignment)

    def test_return_default_if_process_has_result_start_date_but_item_state_is_wrong(
            self, item, item_workflow_sheet, process, process_workflow_sheet, registry):
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        registry.content.get_sheet.side_effect = [process_workflow_sheet, item_workflow_sheet]
        process_workflow_sheet.get.return_value = {'state_data': []}
        item_workflow_sheet.get.return_value = {'workflow_state': 'WRONG'}
        assert self.call_fut(item, 'default') == 'default'

    def test_return_result_start_date_of_process_if_item_state_is_selected_or_rejected(
            self, item, item_workflow_sheet, process, process_workflow_sheet, registry):
        from datetime import datetime
        registry.content.get_sheet.side_effect = [process_workflow_sheet, item_workflow_sheet]
        process_workflow_sheet.get.return_value = {'state_data': []}
        item_workflow_sheet.get.return_value = {'workflow_state': 'selected'}
        decision_date = datetime.now()
        process_workflow_sheet.get.return_value =\
            {'state_data': [{'name': 'result',
                             'start_date': decision_date}]}
        assert self.call_fut(item, 'default') == decision_date

    @mark.usefixtures('integration')
    def test_register(self, registry):
        from adhocracy_s1.resources.s1 import IProposal
        from substanced.interfaces import IIndexView
        assert registry.adapters.lookup((IProposal,), IIndexView,
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
