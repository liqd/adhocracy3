from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


class TestState:

    @fixture
    def inst(self):
        from adhocracy_core.workflows.schemas import StateMeta
        return StateMeta()

    def test_state_deserialize_empty(self, inst):
        assert inst.deserialize({}) == {'title': '',
                                        'description': '',
                                        'display_only_to_roles': [],
                                        'acl': []}


class TestTransition:

    @fixture
    def inst(self):
        from adhocracy_core.workflows.schemas import TransitionMeta
        return TransitionMeta()

    @fixture
    def required_cstruct(self):
        return {'from_state': 'test',
                'to_state': 'test'}

    def test_required_fields(self, inst):
        assert inst['from_state'].required
        assert inst['to_state'].required

    def test_deserialize_required(self, inst, required_cstruct):
        result = inst.deserialize(required_cstruct)
        assert result['from_state'] == 'test'
        assert result['to_state'] == 'test'
        assert result['permission'] == ''
        assert result['callback'] == None

    def test_deserialize_callback(self, inst, required_cstruct):
        from copy import copy
        cstruct = required_cstruct
        cstruct['callback'] = 'copy.copy'
        result = inst.deserialize(cstruct)
        assert result['callback'] == copy

    def test_serialize_required(self, inst, required_cstruct):
        result = inst.serialize(required_cstruct)
        assert result['from_state'] == 'test'
        assert result['to_state'] == 'test'
        assert result['permission'] == ''
        assert result['callback'] == None

    def test_serialize_callback(self, inst, required_cstruct):
        from copy import copy
        cstruct = required_cstruct
        cstruct['callback'] = copy
        result = inst.serialize(cstruct)
        assert result['callback'] == 'copy'


class TestWorkflow:

    @fixture
    def inst(self):
        from adhocracy_core.workflows.schemas import WorkflowMeta
        return WorkflowMeta()

    @fixture
    def required_cstruct(self) -> dict:
        return \
            {'states_order': ['announced'],
             'states': {'announced': {}},
             'transitions': {'to_announced': {'from_state': 'announced',
                                              'to_state': 'announced',
                                              }},
             }

    def test_required_fields(self, inst):
        assert inst['states_order'].required
        assert inst['states'].required
        assert inst['transitions'].required

    def test_deserialize_required(self, inst, required_cstruct):
        result = inst.deserialize(required_cstruct)
        assert result['states_order']
        assert len(result['states']) == 1
        assert len(result['transitions']) == 1


def test_create_workflow_meta_add_transition_and_state_meta():
    from .schemas import TransitionMeta
    from .schemas import StateMeta
    from .schemas import create_workflow_meta_schema
    data = {'transitions': {'to_draft': {}},
            'states': {'draft': {}}}
    node = create_workflow_meta_schema(data)
    assert isinstance(node['transitions']['to_draft'], TransitionMeta)
    assert isinstance(node['states']['draft'], StateMeta)

    # TODO More validators for sanity checks
