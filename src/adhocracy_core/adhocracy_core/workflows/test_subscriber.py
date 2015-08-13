from pyramid import testing
from pytest import mark
from pytest import fixture


@fixture
def registry(registry_with_content):
    return registry_with_content


class TestInitWorkflow:


    @fixture
    def event(self, context, registry):
        event = testing.DummyResource(object=context,
                                      registry=registry)
        return event

    def call_fut(self, event):
        from .subscriber import initialize_workflow
        return initialize_workflow(event)

    def test_ignore_if_already_initialized(self, event, registry, mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.has_state.return_value = True
        self.call_fut(event)
        assert not mock_workflow.initialize.called

    def test_ignore_if_resource_type_without_workflow(self, event, registry, mock_workflow):
        registry.content.get_workflow.return_value =  None
        self.call_fut(event)
        assert not mock_workflow.initialize.called

    def test_initalize(self, event, registry, mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.has_state.return_value = False
        self.call_fut(event)
        assert mock_workflow.initialize.called_with(event.object)


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.workflows.subscriber')


@mark.usefixtures('integration')
def test_register_subscriber(registry):
    from .subscriber import initialize_workflow
    handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
    assert initialize_workflow.__name__ in handlers


