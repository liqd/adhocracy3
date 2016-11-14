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


class TestACLocalRolesState:

    def make_one(self, **kwargs):
        from . import ACLLocalRolesState
        return ACLLocalRolesState(**kwargs)

    def test_call_empty(self, context, mocker):
        set_acl = mocker.patch('adhocracy_core.workflows.set_acl')
        add_roles = mocker.patch('adhocracy_core.workflows.add_local_roles')
        inst = self.make_one()
        inst(context, None, None, None)
        assert not set_acl.called
        assert not add_roles.called

    def test_call_with_acl(self, context, mocker, request_):
        set_acl = mocker.patch('adhocracy_core.workflows.set_acl')
        inst = self.make_one(acl=[])
        inst(context, request_, None, None)
        set_acl.assert_called_with(context, [], request_.registry)

    def test_call_with_local_roles(self, context, mocker, request_):
        add_local_roles = mocker.patch('adhocracy_core.workflows.add_local_roles')
        inst = self.make_one(local_roles={})
        inst(context, request_, None, None)
        add_local_roles.assert_called_with(context, {},
                                           request_.registry)


class TestAdhocracyACLWorkflow:

    @fixture
    def inst(self):
        from . import ACLLocalRolesWorkflow
        inst = ACLLocalRolesWorkflow('draft', 'sample', )
        return inst

    def test_create(self, inst):
        from substanced.workflow import IWorkflow
        from adhocracy_core.interfaces import IAdhocracyWorkflow
        from . import ACLLocalRolesState
        assert inst._state_factory == ACLLocalRolesState
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

    def test_update_state_acl(self, inst, context, mock_workflow):
        from substanced.workflow import ACLState
        mock_workflow.state_of.return_value = 'state_name'
        state = ACLState(acl=['Deny', 'view', 'role:admin'])
        mock_workflow._states = {'state_name': state}
        fut = inst.__class__.update_acl
        fut(mock_workflow, context)
        assert context.__acl__ == ['Deny', 'view', 'role:admin']


class TestUpdateWorkflowStateACLs:

    def call_fut(self, *args):
        from . import update_workflow_state_acls
        return update_workflow_state_acls(*args)

    @fixture
    def mock_catalogs(self, mocker, mock_catalogs):
        mocker.patch('adhocracy_core.workflows.find_service',
                     return_value=mock_catalogs)
        return mock_catalogs

    def test_ignore_if_no_resources_with_workflow_assignment(
        self, context, registry, mock_catalogs, query):
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        self.call_fut(context, registry)
        mock_catalogs.search.call_args[0][0] ==\
            query._replace(interfaces=IWorkflowAssignment)

    def test_ignore_if_only_resources_with_empty_workflow_assignment(
        self, context, registry, mock_catalogs, search_result, mock_workflow, pool):
        mock_catalogs.search.return_value =\
            search_result._replace(elements=(x for x in [pool]))
        registry.content.get_workflow.return_value = None
        self.call_fut(context, registry)
        assert not mock_workflow.update_acl.called

    def test_reset_local_permissions_of_current_workflow_state(
        self, context, registry, mock_catalogs, search_result, mock_workflow, pool):
        mock_catalogs.search.return_value =\
            search_result._replace(elements=(x for x in [pool]))
        registry.content.get_workflow.return_value = mock_workflow
        self.call_fut(context, registry)
        assert mock_workflow.update_acl.called


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
        from adhocracy_core.workflows import ACLLocalRolesWorkflow
        mock = Mock(spec=ACLLocalRolesWorkflow)
        monkeypatch.setattr('adhocracy_core.workflows.ACLLocalRolesWorkflow',
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
        from . import ACLLocalRolesWorkflow
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        workflow = registry.content.workflows['dummy']
        assert workflow.type == 'dummy'
        assert isinstance(workflow, ACLLocalRolesWorkflow)

    def test_create_and_add_states(self, registry, mock_meta):
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        workflow = registry.content.workflows['dummy']
        states = sorted(workflow.get_states(None, None),
                        key=lambda x: x['name'])
        assert states[0]['initial'] is False
        assert workflow._states['draft'].acl == [('Deny', 'role:moderator', 'view')]
        assert workflow._states['draft'].local_roles is None
        assert states[1]['initial'] is True

    def test_create_and_add_states_with_local_roles(self, registry, mock_meta):
        from adhocracy_core.interfaces import DEFAULT_USER_GROUP_NAME
        mock_meta.return_value['add_local_role_participant_to_default_group'] = True
        self.call_fut(registry, 'package:dummy.yaml', 'dummy')
        workflow = registry.content.workflows['dummy']
        assert workflow._states['draft'].local_roles == \
               {'group:' + DEFAULT_USER_GROUP_NAME: {'role:' + 'participant'}}

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

