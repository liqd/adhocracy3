from pyramid import testing
from pytest import mark
from pytest import fixture


class TestInitWorkflow:

    @fixture
    def registry(self, mock_content_registry, mock_workflow):
        mock_content_registry.workflows_meta['sample'] = {'workflow': mock_workflow}
        registry = testing.DummyResource(content=mock_content_registry)
        return registry

    @fixture
    def context(self):
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        context = testing.DummyResource(__provides__=IWorkflowAssignment)
        return context

    @fixture
    def event(self, context, registry):
        event = testing.DummyResource(object=context,
                                      registry=registry)
        return event

    def call_fut(self, event):
        from .subscriber import initialize_workflows
        return initialize_workflows(event)

    def test_ignore_if_already_initialized(self, event, mock_workflow, mock_sheet):
        mock_sheet.get.return_value = {'workflow': mock_workflow}
        event.registry.content.get_sheet.return_value = mock_sheet
        mock_workflow.has_state.return_value = True
        self.call_fut(event)
        assert not mock_workflow.initialize.called

    def test_initalize(self, event, mock_workflow, mock_sheet):
        mock_sheet.get.return_value = {'workflow': mock_workflow}
        event.registry.content.get_sheet.return_value = mock_sheet
        mock_workflow.has_state.return_value = False
        self.call_fut(event)
        assert mock_workflow.initialize.called_with(event.object)


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.workflows.subscriber')


@mark.usefixtures('integration')
def test_register_subscriber(registry):
    from .subscriber import initialize_workflows
    handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
    assert initialize_workflows.__name__ in handlers


