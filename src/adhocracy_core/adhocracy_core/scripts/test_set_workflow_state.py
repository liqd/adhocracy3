from unittest.mock import Mock
from pytest import fixture


@fixture
def transaction_mock(monkeypatch):
    mock = Mock()
    monkeypatch.setattr('adhocracy_core.scripts.set_workflow_state.transaction',
                        mock)
    return mock


@fixture
def transition_to_mock(monkeypatch):
    import adhocracy_core.workflows
    mock = Mock(spec=adhocracy_core.workflows.transition_to_states)
    monkeypatch.setattr('adhocracy_core.scripts.set_workflow_state.transition_to_states',
                        mock)
    return mock

@fixture
def print_mock(monkeypatch):
    import builtins
    mock = Mock(spec=builtins.print)
    monkeypatch.setattr('builtins.print', mock)
    return mock


def test_set_workflow_state(registry, context, transaction_mock,
                            transition_to_mock):
    from .set_workflow_state import _set_workflow_state
    _set_workflow_state(context, registry, '/', ['announced', 'participate'])

    transition_to_mock.assert_called_with(context, ['announced', 'participate'],
                                          registry)
    assert transaction_mock.commit.called


def test_set_workflow_state_with_reset(registry, context, transition_to_mock):
    from .set_workflow_state import _set_workflow_state
    _set_workflow_state(context, registry, '/', [], reset=True)
    transition_to_mock.assert_called_with(context, [], registry, reset=True)

def test_set_workflow_state_with_absolute(registry_with_content, context, transition_to_mock):
    registry = registry_with_content
    workflow_mock = Mock()
    state_of_mock = Mock(side_effect=['draft', 'participate'])
    workflow_mock.state_of = state_of_mock
    registry.content.get_workflow.return_value = workflow_mock
    from .set_workflow_state import _set_workflow_state
    _set_workflow_state(context, registry, '/', ['announced', 'participate'], absolute=True)
    transition_to_mock.assert_called_with(context, ['announced', 'participate'], registry)

    _set_workflow_state(context, registry, '/', ['announced', 'participate', 'result'], absolute=True)
    transition_to_mock.assert_called_with(context, ['result'], registry)

def test_print_workflow_info(registry_with_content, context, print_mock):
    registry = registry_with_content
    workflow_mock = Mock(type='standard')
    registry.content.get_workflow.return_value = workflow_mock
    registry.content.workflows_meta = {'standard': {'states': {'draft': None, 'announced': None}}}
    from .set_workflow_state import _print_workflow_info
    _print_workflow_info(context, registry, '/')
    assert print_mock.called
