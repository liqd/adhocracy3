from pyramid import testing
from unittest.mock import Mock
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.workflows')


@mark.usefixtures('integration')
class TestSetupWorkflow:

    def _make_workflow(self, registry, name):
        from adhocracy_core.workflows import add_workflow
        cstruct = \
            {'states_order': ['draft', 'announced', 'participate'],
             'states': {'draft': {'acm': {'principals':           ['moderator'],
                                          'permissions': [['view', 'Deny']]}},
                        'announced': {'acl': []},
                        'participate': {'acl': []}},
             'transitions': {'to_announced': {'from_state': 'draft',
                                              'to_state': 'announced',
                                              'permission': 'do_transition',
                                              'callback': None,
                                              },
                             'to_participate': {'from_state': 'announced',
                                                'to_state': 'participate',
                                                'permission': 'do_transition',
                                                'callback': None,
                             }},
             }
        return add_workflow(registry, cstruct, name)

    def test_set_workflow_state(self, registry, context, monkeypatch):
        import adhocracy_core.scripts.set_workflow_state
        setup_workflow_mock = Mock(spec=adhocracy_core.workflows.setup_workflow)
        transaction_mock = Mock()
        monkeypatch.setattr(adhocracy_core.scripts.set_workflow_state,
                            'setup_workflow',
                            setup_workflow_mock)
        monkeypatch.setattr(adhocracy_core.scripts.set_workflow_state,
                            'transaction',
                            transaction_mock)
        from .set_workflow_state import _set_workflow_state
        self._make_workflow(registry, 'test_workflow')
        process = testing.DummyResource()
        context['organisation'] = process
        _set_workflow_state(context, registry, '/organisation', 'test_workflow', 'participate')
        setup_workflow_mock.assert_called_with(registry.content.workflows['test_workflow'],
                                               process,
                                               ['announced', 'participate'],
                                               registry)
        assert transaction_mock.commit.called
