from unittest.mock import Mock
from pyramid import testing
from pytest import fixture
from pytest import raises


class TestAdhocracyACLWorkflow:

    @fixture
    def request(self):
        return testing.DummyResource()

    @fixture
    def inst(self):
        from . import AdhocracyACLWorkflow
        inst = AdhocracyACLWorkflow('draft', 'sample')
        return inst

    def test_create(self, inst):
        from substanced.workflow import IWorkflow
        from adhocracy_core.interfaces import IAdhocracyWorkflow
        assert IWorkflow.providedBy(inst)
        assert IAdhocracyWorkflow.providedBy(inst)
        from zope.interface.verify import verifyObject
        assert verifyObject(IAdhocracyWorkflow, inst)

    def test_get_next_states(self, inst, context, request, mock_workflow):
        fut = inst.__class__.get_next_states
        mock_workflow.state_of.return_value = 'draft'
        mock_workflow.get_transitions.return_value = [{'to_state': 'announced'}]
        assert fut(mock_workflow, context, request) == ['announced']
        assert mock_workflow.get_transitions.called_with(context, request,
                                                         from_state='draft')


class TestAddWorkflow:

    @fixture
    def registry(self, mock_content_registry):
        registry = testing.DummyResource(content=mock_content_registry)
        return registry

    @fixture
    def cstruct(self) -> dict:
        """Return example workflow cstruct with required data."""
        cstruct = \
            {'states_order': ['draft', 'announced'],
             'states': {'draft': {'acl': [('Deny', 'reader', ['view'])]},
                        'announced': {'acl': []}},
             'transitions': {'to_announced': {'from_state': 'draft',
                                              'to_state': 'announced',
                                              'permission': 'do_transition',
                                              'callback': None,
                                              }},
             }
        return cstruct

    def call_fut(self, registry, cstruct, name):
        from .sample import add_workflow
        return add_workflow(registry, cstruct, name)

    def test_add_cstruct_to_workflows_meta(self, registry, cstruct):
        self.call_fut(registry, cstruct, 'sample')
        meta = registry.content.workflows_meta['sample']
        assert 'name' not in meta
        assert meta['states']
        assert meta['transitions']
        assert meta['states_order']

    def test_create_workflow_and_add_to_workflows_meta(self, registry, cstruct):
        from substanced.workflow import ACLWorkflow
        self.call_fut(registry, cstruct, 'sample')
        workflow = registry.content.workflows['sample']
        assert workflow.type == 'sample'
        assert isinstance(workflow, ACLWorkflow)

    def test_create_workflow_and_add_states(self, registry, cstruct):
        self.call_fut(registry, cstruct, 'sample')
        workflow = registry.content.workflows['sample']
        states = sorted(workflow.get_states(None, None),
                        key=lambda x: x['name'])
        assert states[0]['initial'] is False
        assert workflow._states['draft'].acl == [('Deny', 'role:reader', ['view'])]
        assert states[1]['initial'] is True
        assert workflow._states['announced'].acl == []

    def test_create_workflow_and_add_transitions(self, registry, cstruct):
        self.call_fut(registry, cstruct, 'sample')
        workflow = registry.content.workflows['sample']
        transition_data = cstruct['transitions']['to_announced']
        transition_data['name'] = 'to_announced'
        assert workflow._transitions['to_announced'] == transition_data

    def test_raise_if_cstruct_not_valid(self, registry, cstruct):
        from adhocracy_core.exceptions import ConfigurationError
        del cstruct['transitions']['to_announced']['from_state']
        with raises(ConfigurationError) as err:
            self.call_fut(registry, cstruct, 'sample')
        assert 'Required' in err.value.__str__()

    @fixture
    def mock_workflow(self, monkeypatch):
        from adhocracy_core.workflows import AdhocracyACLWorkflow
        mock = Mock(spec=AdhocracyACLWorkflow)
        monkeypatch.setattr('adhocracy_core.workflows.AdhocracyACLWorkflow',
                            mock)
        return mock

    def test_create_workflow_and_check(self, registry, cstruct, mock_workflow):
        self.call_fut(registry, cstruct, 'sample')
        assert mock_workflow.return_value.check.called

    def test_raise_if_workflow_error(self, registry, cstruct, mock_workflow):
        from substanced.workflow import WorkflowError
        from adhocracy_core.exceptions import ConfigurationError
        mock_workflow.return_value.check.side_effect = WorkflowError('msg')
        with raises(ConfigurationError) as err:
            self.call_fut(registry, cstruct, 'sample')
        assert 'msg' in err.value.__str__()
