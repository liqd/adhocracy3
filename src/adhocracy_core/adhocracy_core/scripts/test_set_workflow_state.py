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


def test_set_workflow_state(registry, context, transaction_mock,
                            transition_to_mock):
    from .set_workflow_state import _set_workflow_state
    _set_workflow_state(context, registry, '/', ['announced', 'participate'])

    transition_to_mock.assert_called_with(context, ['announced', 'participate'],
                                          registry)
    assert transaction_mock.commit.called
