from datetime import datetime
from pyramid import testing
from unittest.mock import Mock
from pytest import fixture


class TestAutoTransitionWorkflow:

    def call_fut(self, *args):
        from .ad_auto_transition_process_workflow import auto_transition_process_workflow
        return auto_transition_process_workflow(*args)

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    @fixture
    def mock_catalogs(self, mocker, mock_catalogs):
        mocker.patch(
            'adhocracy_core.scripts.ad_auto_transition_process_workflow.'
            'find_service',
            return_value = mock_catalogs)
        return mock_catalogs

    @fixture
    def mock_process(self):
        return testing.DummyResource()

    @fixture
    def mock_catalogs_with_process(self, search_result, mock_catalogs,
                                   mock_process):
        mock_catalogs.search.side_effect = [
            search_result._replace(elements=[mock_process])]
        return mock_catalogs

    @fixture
    def mock_transition_to_states(self, registry, mocker):
        mock = mocker.patch(
            'adhocracy_core.scripts.ad_auto_transition_process_workflow.'
            'transition_to_states')
        return mock

    @fixture
    def mock_workflow(self, registry, mock_workflow):
        mock_workflow.type = 'standard'
        mock_workflow.get_next_states.return_value = ['evaluate']
        registry.content.get_workflow = Mock(return_value=mock_workflow)
        return mock_workflow

    @fixture
    def mock_now(self, mocker):
        mock = mocker.patch(
            'adhocracy_core.scripts.ad_auto_transition_process_workflow.now',
            return_value = datetime(2016, 1, 5))
        return mock

    def test_ignore_no_processes(self, context, registry, mocker,
            mock_catalogs, mock_transition_to_states):
        self.call_fut(context, registry)
        assert not mock_transition_to_states.called

    def test_ignore_processes_without_auto_transition(self, context, registry,
            mock_catalogs_with_process, search_result,
            mock_transition_to_states, mock_sheet, mock_workflow):
        registry.content.workflows_meta = {
                'standard': {'auto_transition': False}}
        mock_sheet.get.return_value = {
            'workflow': mock_workflow
            }
        registry.content.get_sheet = Mock(return_value=mock_sheet)
        self.call_fut(context, registry)
        assert not mock_transition_to_states.called

    def test_ignore_processes_currently_active(self, context, registry,
            mock_catalogs_with_process, search_result,
            mock_transition_to_states, mock_sheet, mock_workflow):
        registry.content.workflows_meta = {
            'standard': {'auto_transition': False}}
        mock_sheet.get.return_value = {
            'workflow': mock_workflow,
            'workflow_state': 'participate',
            'state_data': [
                {'name': 'participate', 'description': '',
                 'start_date': datetime(2016, 1, 1)},
                {'name': 'evaluate', 'description': '',
                 'start_date': datetime(2016, 1, 10)}
            ]}
        registry.content.get_sheet = Mock(return_value=mock_sheet)
        self.call_fut(context, registry)
        assert not mock_transition_to_states.called

    def test_ignore_multiple_next_states(self, context, registry,
            mock_catalogs, search_result, mock_transition_to_states,
            mock_sheet, mock_workflow, mock_now):
        process = testing.DummyResource()
        mock_catalogs.search.side_effect = [
            search_result._replace(elements=[process]),
            search_result]
        registry.content.workflows_meta = {
            'standard': {'auto_transition': True}}
        mock_sheet.get.return_value = {
            'workflow': mock_workflow,
            'workflow_state': 'participate',
            'state_data': []}
        registry.content.get_sheet = Mock(return_value=mock_sheet)
        mock_workflow.get_next_states.return_value = ['evaluate1', 'evaluate2']
        self.call_fut(context, registry)
        assert not mock_transition_to_states.called

    def test_ignore_empty_state_data(self, context, registry,
            mock_catalogs, search_result, mock_transition_to_states,
            mock_sheet, mock_workflow, mock_now):
        process = testing.DummyResource()
        mock_catalogs.search.side_effect = [
            search_result._replace(elements=[process]),
            search_result]
        registry.content.workflows_meta = {
            'standard': {'auto_transition': True}}
        mock_sheet.get.return_value = {
            'workflow': mock_workflow,
            'workflow_state': 'participate',
            'state_data': []}
        registry.content.get_sheet = Mock(return_value=mock_sheet)
        self.call_fut(context, registry)
        assert not mock_transition_to_states.called

    def test_transition_needed_by_next_state(self, context, registry,
            mock_catalogs_with_process, mock_process, search_result,
            mock_transition_to_states, mock_sheet, mock_workflow, mock_now):
        registry.content.workflows_meta = {
            'standard': {'auto_transition': True}}
        mock_sheet.get.return_value = {
            'workflow': mock_workflow,
            'workflow_state': 'participate',
            'state_data': [
                {'name': 'participate', 'description': '',
                 'start_date': datetime(2016, 1, 1)},
                {'name': 'evaluate', 'description': '',
                 'start_date': datetime(2016, 1, 3)}
            ]}
        registry.content.get_sheet = Mock(return_value=mock_sheet)
        self.call_fut(context, registry)
        mock_transition_to_states.assert_called_with(
            mock_process, ['evaluate'], registry)
