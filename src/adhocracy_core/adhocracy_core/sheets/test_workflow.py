from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.workflow')


@fixture
def registry(registry_with_content):
    return registry_with_content


class TestWorkflow:

    @fixture
    def inst(self):
        from .workflow import Workflow
        return Workflow()

    def test_create(self, inst):
        from adhocracy_core.schema import AdhocracySchemaNode
        assert isinstance(inst, AdhocracySchemaNode)
        assert inst.readonly

    def test_serialize_default_workflow_is_none(self, inst):
        inst = inst.bind(workflow=None)
        assert inst.serialize() == ''

    def test_serialize_default(self, inst, mock_workflow):
        mock_workflow.type = 'w'
        inst = inst.bind(workflow=mock_workflow)
        assert inst.serialize() == 'w'

    def test_serialize_workflow(self, inst, mock_workflow):
        mock_workflow.type = 'w'
        inst = inst.bind(workflow=mock_workflow)
        assert inst.serialize(mock_workflow) == 'w'


class TestState:

    @fixture
    def inst(self):
        from .workflow import State
        return State()

    def test_create(self, inst):
        from adhocracy_core.schema import SingleLine
        assert isinstance(inst, SingleLine)

    def test_serialize_default_workflow_is_none(self, inst):
        inst = inst.bind(workflow=None)
        assert inst.serialize() == ''

    def test_serialize_default_state_is_none(self, inst, mock_workflow, context):
        mock_workflow.state_of.return_value = None
        inst = inst.bind(workflow=mock_workflow, context=context)
        assert inst.serialize() == ''

    def test_deserialize_raise_if_wrong_state(self, inst, context, mock_workflow):
        from colander import Invalid
        request_ = testing.DummyRequest()
        mock_workflow.get_next_states.return_value = []
        inst = inst.bind(workflow=mock_workflow, context=context,
                         request=request_)
        with raises(Invalid):
            inst.deserialize('announced')

    def test_deserialize(self, inst, context, registry, mock_workflow, request):
        inst = inst.bind(workflow=mock_workflow, context=context)
        mock_workflow.get_next_states.return_value = ['announced']
        assert inst.deserialize('announced') == 'announced'
        assert mock_workflow.get_next_states.called_with(context, request)


class TestStateName:

    @fixture
    def inst(self):
        from .workflow import StateName
        return StateName()

    def test_create(self, inst):
        from adhocracy_core.schema import SingleLine
        assert isinstance(inst, SingleLine)

    def test_serialize(self, inst, node):
        assert inst.serialize('state') == 'state'

    def test_deserialize(self, inst, context, mock_workflow):
        mock_workflow._states = {'draft': {}}
        inst = inst.bind(workflow=mock_workflow, context=context)
        assert inst.deserialize('draft') == 'draft'


def test_state_data_create():
    from adhocracy_core import schema
    from . import workflow
    inst = workflow.StateData()
    assert isinstance(inst['name'], workflow.StateName)
    assert isinstance(inst['start_date'], schema.DateTime)
    assert isinstance(inst['description'], schema.Text)


def test_state_data_list():
    from . import workflow
    inst = workflow.StateDataList()
    assert isinstance(inst['data'], workflow.StateData)


def test_workflow_assignment_schema_create():
    from . import workflow
    inst = workflow.WorkflowAssignmentSchema()
    assert isinstance(inst['workflow'], workflow.Workflow)
    assert isinstance(inst['workflow_state'], workflow.State)
    assert isinstance(inst['state_data'], workflow.StateDataList)


class TestWorkflowAssignmentSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.workflow import workflow_meta
        return workflow_meta

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        from adhocracy_core.sheets.workflow import WorkflowAssignmentSheet
        from adhocracy_core.sheets.workflow import WorkflowAssignmentSchema
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, WorkflowAssignmentSheet)
        assert inst.meta.isheet == IWorkflowAssignment
        assert inst.meta.schema_class == WorkflowAssignmentSchema
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_create_raise_if_wrong_isheet(self, meta, context):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.exceptions import RuntimeConfigurationError
        meta = meta._replace(isheet=ISheet)
        with raises(RuntimeConfigurationError):
            meta.sheet_class(meta, context)

    def test_create_raise_if_wrong_schema(self, meta, context):
        from colander import MappingSchema
        from adhocracy_core.exceptions import RuntimeConfigurationError
        meta = meta._replace(schema_class=MappingSchema)
        with raises(RuntimeConfigurationError):
            meta.sheet_class(meta, context)

    def test_get_empty_without_workflow(self, meta, context, registry):
        registry.content.get_workflow.return_value = None
        inst = meta.sheet_class(meta, context, registry)
        assert inst.get() == {'workflow': None,
                              'workflow_state': '',
                              'state_data': []}

    def test_get_empty_with_workflow(self, meta, context, registry,
                                    mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.type = 'w'
        mock_workflow.state_of.return_value = 'draft'
        inst = meta.sheet_class(meta, context, registry)
        assert inst.get() == {'workflow': mock_workflow,
                              'workflow_state': 'draft',
                              'state_data': []}

    def test_get_cstruct_empty_without_workflow(self, meta, context, registry):
        registry.content.get_workflow.return_value = None
        inst = meta.sheet_class(meta, context, registry=registry)
        request = testing.DummyRequest(registry=registry)
        assert inst.get_cstruct(request) == {'workflow': '',
                                             'workflow_state': '',
                                             'state_data': []}

    def test_get_cstruct_empty_with_workflow(self, meta, context, registry,
                                             mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.type = 'w'
        mock_workflow.state_of.return_value = 'draft'
        inst = meta.sheet_class(meta, context, registry=registry)
        request = testing.DummyRequest(registry=registry)
        assert inst.get_cstruct(request) == {'workflow': 'w',
                                             'workflow_state': 'draft',
                                             'state_data': []}


    def test_set_workflow_state(self, meta, context, registry, mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow._states = {'announced': {}}
        inst = meta.sheet_class(meta, context, registry=registry)
        inst.set({'workflow_state': 'announced'})
        call_args = mock_workflow.transition_to_state.call_args
        assert call_args[0][0] is inst.context
        assert isinstance(call_args[0][1], testing.DummyRequest)
        assert call_args[1] == {'to_state': 'announced'}

    def test_set_other(self, meta, context, registry, mock_workflow):
        from colander import MappingSchema
        registry.content.get_workflow.return_value = mock_workflow
        inst = meta.sheet_class(meta, context, registry=registry)
        inst.schema = inst.schema.clone()
        inst.schema.add(MappingSchema(name='other'))
        inst.set({'other': {}})
        assert 'other' in inst._data

    def tesget_next_states(self, meta, context, registry, mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.get_next_states.return_value = ['announced']
        inst = meta.sheet_class(meta, context, registry=registry)
        request = testing.DummyRequest()
        assert inst.get_next_states(request) == ['announced']
        mock_workflow.get_next_states.assert_called_with(inst.context, request)

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)
