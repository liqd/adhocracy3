from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises
from unittest.mock import Mock
import pytest
from substanced.workflow import WorkflowError


@fixture
def registry(registry_with_content):
    return registry_with_content


class TestAdhocracyACLWorkflow:

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

    def test_get_next_states_with_two_transitions_same_state(
            self, inst, context, request, mock_workflow):
        fut = inst.__class__.get_next_states
        mock_workflow.state_of.return_value = 'draft'
        mock_workflow.get_transitions.return_value = [{'to_state': 'announced'},
                                                      {'to_state': 'announced'}]
        assert fut(mock_workflow, context, request) == ['announced']
        assert mock_workflow.get_transitions.called_with(context, request,
                                                         from_state='draft')


class TestAddWorkflow:

    @fixture
    def registry(self, mock_content_registry):
        registry = Mock(content=mock_content_registry)
        registry.content.permissions = ['view']
        return registry

    @fixture
    def mock_meta(self, mocker) -> Mock:
        cstruct = \
            {'initial_state': 'draft',
             'auto_transition': False,
             'states': {'draft': {'acm': {'principals':           ['moderator'],
                                          'permissions': [['view', 'Deny']]}},
                        'announced': {}},
             'transitions': {'to_announced': {'from_state': 'draft',
                                              'to_state': 'announced',
                                              'permission': 'do_transition',
                                              'callback': None,
                                              }},
             }
        mock = mocker.patch('adhocracy_core.workflows._get_meta')
        mock.return_value = cstruct
        return mock

    @fixture
    def mock_workflow(self, monkeypatch):
        from adhocracy_core.workflows import AdhocracyACLWorkflow
        mock = Mock(spec=AdhocracyACLWorkflow)
        monkeypatch.setattr('adhocracy_core.workflows.AdhocracyACLWorkflow',
                            mock)
        return mock

    def call_fut(self, *args):
        from . import add_workflow
        return add_workflow(*args)

    def test_add_meta(self, registry, mock_meta):
        from pyrsistent import PMap
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        meta = registry.content.workflows_meta['dummy']
        assert isinstance(meta, PMap)
        assert meta['states']
        assert meta['transitions']
        assert meta['initial_state']
        assert meta['auto_transition'] is False

    def test_create(self, registry, mock_meta):
        from substanced.workflow import ACLWorkflow
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        workflow = registry.content.workflows['dummy']
        assert workflow.type == 'dummy'
        assert isinstance(workflow, ACLWorkflow)

    def test_create_and_add_states(self, registry, mock_meta):
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        workflow = registry.content.workflows['dummy']
        states = sorted(workflow.get_states(None, None),
                        key=lambda x: x['name'])
        assert states[0]['initial'] is False
        assert workflow._states['draft'].acl == [('Deny', 'role:moderator', 'view')]
        assert states[1]['initial'] is True

    def test_create_and_add_transitions(self, registry, mock_meta):
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        workflow = registry.content.workflows['dummy']
        assert workflow._transitions['to_announced']['name'] == 'to_announced'

    def test_raise_if_cstruct_not_valid(self, registry, mock_meta, mocker, node):
        import colander
        from adhocracy_core.exceptions import ConfigurationError
        mock = mocker.patch('colander.MappingSchema.deserialize')
        mock.side_effect = colander.Invalid(node)
        with raises(ConfigurationError) as err:
            self.call_fut(registry, 'package:dummy.yaml', 'dummy')

    def test_create_and_check(self, registry, mock_meta, mock_workflow):
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        assert mock_workflow.return_value.check.called

    def test_raise_if_workflow_error(self, registry, mock_meta, mock_workflow):
        from substanced.workflow import WorkflowError
        from adhocracy_core.exceptions import ConfigurationError
        mock_workflow.return_value.check.side_effect = WorkflowError('msg')
        with raises(ConfigurationError) as err:
            self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        assert 'msg' in err.value.__str__()

    def test_add_meta_with_defaults(self, registry, mock_meta):
        from pyrsistent import freeze
        standard_meta = freeze(mock_meta.return_value)\
            .transform(['states', 'draft', 'acm', 'principals'], ['role:moderator'])
        registry.content.workflows_meta['standard'] = standard_meta
        mock_meta.return_value = {'defaults': 'standard'}
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        meta = registry.content.workflows_meta['dummy']
        assert meta['states'] == standard_meta['states']
        assert meta['transitions'] == standard_meta['transitions']
        assert meta['initial_state'] == standard_meta['initial_state']
        assert meta['defaults'] == 'standard'

    def test_add_meta_with_defaults_inital_state(self, registry, mock_meta):
        from pyrsistent import freeze
        standard_meta = freeze(mock_meta.return_value)\
            .transform(['states', 'draft', 'acm', 'principals'], ['role:moderator'])
        registry.content.workflows_meta['standard'] = standard_meta
        mock_meta.return_value = \
            {'defaults': 'standard',
             'initial_state': 'announced'}
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        meta = registry.content.workflows_meta['dummy']
        assert meta['initial_state'] == 'announced'

    def test_add_meta_with_defaults_transitions(self, registry, mock_meta):
        from pyrsistent import freeze
        standard_meta = freeze(mock_meta.return_value)\
            .transform(['states', 'draft', 'acm', 'principals'], ['role:moderator'])
        registry.content.workflows_meta['standard'] = standard_meta
        mock_meta.return_value = \
            {'defaults': 'standard',
             'transitions': {'to_announced2': {'to_state': 'announced',
                                               'from_state': 'draft'}
             }}
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        meta = registry.content.workflows_meta['dummy']
        assert meta['transitions']['to_announced2']

    def test_add_meta_with_defaults_state_edit_permission(self, registry,
                                                           mock_meta):
        from pyrsistent import freeze
        standard_meta = freeze(mock_meta.return_value)\
            .transform(['states', 'draft', 'acm', 'principals'], ['role:moderator'])
        registry.content.workflows_meta['standard'] = standard_meta
        mock_meta.return_value =\
            {'defaults': 'standard',
             'states': {'draft': {'acm': {'permissions':[['view', 'Edited']]}}
             }}
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        meta = registry.content.workflows_meta['dummy']
        assert meta['states']['draft']['acm']['permissions'] ==\
               [['view', 'Edited']]

    def test_add_meta_with_defaults_state_add_permission(self, registry,
                                                         mock_meta):
        from pyrsistent import freeze
        standard_meta = freeze(mock_meta.return_value)\
            .transform(['states', 'draft', 'acm', 'principals'], ['role:moderator'])
        registry.content.workflows_meta['standard'] = standard_meta
        mock_meta.return_value =\
            {'defaults': 'standard',
             'states': {'draft': {'acm': {'permissions':[['new', 'Added']]}}
             }}
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        meta = registry.content.workflows_meta['dummy']
        assert meta['states']['draft']['acm']['permissions'] ==\
               [['view', 'Deny'],
                ['new', 'Added']]


class TestTransitionToStates:

    def call_fut(self, *args, **kwargs):
        from . import transition_to_states
        return transition_to_states(*args, **kwargs)

    @fixture
    def god_request(self, mocker, request_):
        mock = mocker.patch('adhocracy_core.workflows.create_fake_god_request')
        mock.return_value = request_
        return request_

    def test_do_all_transitions_needed_to_set_state(self, context, registry,
                                                    mock_workflow, god_request):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.has_state.return_value = True
        self.call_fut(context, ['announced', 'participate'], registry)
        assert mock_workflow.transition_to_state.call_args_list[0][0] ==\
               (context, god_request, 'announced')
        assert mock_workflow.transition_to_state.call_args_list[1][0] == \
               (context, god_request, 'participate')

    def test_raise_if_state_already_set(self, context, registry,
                                        mock_workflow, god_request):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.has_state.return_value = True
        mock_workflow.transition_to_state.side_effect = WorkflowError
        with pytest.raises(WorkflowError):
            self.call_fut(context, ['announced'], registry)

    def test_optionally_reset_to_initial_state(self, context, registry,
                                               mock_workflow, god_request):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.has_state.return_value = False
        self.call_fut(context, ['announced'], registry)
        mock_workflow.initialize.assert_called_once_with(context)

    def test_initialize_if_has_no_state(self, context, registry,
                                         mock_workflow, god_request):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.has_state.return_value = False
        self.call_fut(context, ['announced'], registry)
        mock_workflow.initialize.assert_called_once_with(context)

