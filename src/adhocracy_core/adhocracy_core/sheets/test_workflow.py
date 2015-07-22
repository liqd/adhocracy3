from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark


class TestWorkflowType:

    @fixture
    def registry(self, mock_content_registry):
        registry = testing.DummyResource(content=mock_content_registry)
        return registry

    @fixture
    def inst(self):
        from .workflow import WorkflowType
        return WorkflowType()

    def test_serialize_null(self, inst, node):
        from colander import null
        assert inst.serialize(node, null) == ''

    def test_serialize_none(self, inst, node):
        assert inst.serialize(node, None) == ''

    def test_serialize(self, inst, node, mock_workflow):
        mock_workflow.type = 'w'
        assert inst.serialize(node, mock_workflow) == 'w'

    def test_deserialize(self, inst, node, registry, mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
        node = node.bind(registry=registry)
        assert inst.deserialize(node, 'w') == mock_workflow

    def test_deserialize_none(self, inst, node, registry):
        node = node.bind(registry=registry)
        assert inst.deserialize(node, '') == None

    def test_deserialize_raise_if_wrong_workflow(self, inst, node, registry):
        from colander import Invalid
        from adhocracy_core.exceptions import RuntimeConfigurationError
        registry.content.get_workflow.side_effect = RuntimeConfigurationError
        node = node.bind(registry=registry)
        with raises(Invalid):
            inst.deserialize(node, 'w')


class TestWorkflow:

    @fixture
    def registry(self, mock_content_registry):
        registry = testing.DummyResource(content=mock_content_registry)
        return registry

    @fixture
    def inst(self):
        from .workflow import Workflow
        return Workflow()

    def test_create(self, inst):
        from .workflow import WorkflowType
        assert inst.readonly is True
        assert inst.schema_type == WorkflowType

    def test_serialize_default(self, inst, registry, mock_workflow):
        mock_workflow.type = 'w'
        registry.content.get_workflow.return_value = mock_workflow
        inst = inst.bind(workflow_name='w', registry=registry)
        assert inst.serialize() == 'w'

    def test_serialize_default_raise_if_wrong_default(self, inst, registry,
                                                      mock_workflow):
        from adhocracy_core.exceptions import RuntimeConfigurationError
        registry.content.get_workflow.side_effect = RuntimeConfigurationError
        with raises(RuntimeConfigurationError):
            inst.bind(workflow_name='w', registry=registry)

    def test_serialize(self, inst, mock_workflow):
        mock_workflow.type = 'w'
        assert inst.serialize(mock_workflow) == 'w'

    def test_deserialize_raise_always(self, inst, registry, mock_workflow):
        from colander import Invalid
        registry.content.workflows['w'] = mock_workflow
        with raises(Invalid):
            inst.deserialize('w')


class TestState:

    @fixture
    def registry(self, mock_content_registry):
        registry = testing.DummyResource(content=mock_content_registry)
        return registry

    @fixture
    def request(self, registry):
        request = testing.DummyResource(registry=registry)
        return request

    @fixture
    def inst(self):
        from .workflow import State
        return State()

    def test_serialize_null(self, inst, node):
        from colander import null
        assert inst.serialize(null) == None

    def test_serialize_none(self, inst, node):
        assert inst.serialize(None) == None

    def test_serialize_no_workflow(self, inst, context, registry):
        inst.workflow_name = ''
        inst = inst.bind(registry=registry, context=context)
        assert inst.serialize() == None

    def test_serialize_raise_if_wrong_workflow(self, inst, context, registry):
        from adhocracy_core.exceptions import RuntimeConfigurationError
        inst.workflow_name = 'WRONG'
        registry.content.get_workflow.side_effect = RuntimeConfigurationError
        with raises(RuntimeConfigurationError):
            inst.bind(registry=registry, context=context)

    def test_serialize_workflow_and_no_state(self, inst, context, registry,
                                             mock_workflow):
        inst.workflow_name = 'w'
        mock_workflow.state_of.return_value = None
        registry.content.get_workflow.return_value = mock_workflow
        inst = inst.bind(registry=registry, context=context)
        assert inst.serialize() == None

    def test_serialize_workflow_and_state(self, inst, registry, context,
                                          mock_workflow):
        inst.workflow_name = 'w'
        mock_workflow.state_of.return_value = 'draft'
        registry.content.get_workflow.return_value = mock_workflow
        inst = inst.bind(registry=registry, context=context)
        assert inst.serialize() == 'draft'

    def test_deserialize_raise_if_wrong_state(self, inst, context, registry,
                                              mock_workflow, request):
        from colander import Invalid
        inst.workflow_name = 'w'
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.get_next_states.return_value = []
        inst = inst.bind(registry=registry, request=request, context=context)
        with raises(Invalid):
            inst.deserialize('announced')

    def test_deserialize(self, inst, context, registry, mock_workflow, request):
        inst.workflow_name = 'w'
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.get_next_states.return_value = ['announced']
        inst = inst.bind(registry=registry, request=request, context=context)
        assert inst.deserialize('announced') == 'announced'
        assert mock_workflow.get_next_states.called_with(
            context, request)


class TestWorkflowAssignmentSchema:

    @fixture
    def inst(self):
        from .workflow import WorkflowAssignmentSchema
        return WorkflowAssignmentSchema()

    def test_create(self, inst):
        assert inst.workflow_name == 'WRONG'
        assert inst['workflow'].default_workflow_name == 'WRONG'
        assert inst['workflow_state'].workflow_name == 'WRONG'


class TestWorkflowAssignmentSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.workflow import workflow_meta
        return workflow_meta

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

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
        assert meta.permission_edit == 'do_transition'

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

    def test_get_empty(self, meta, context, registry, mock_workflow):
        mock_workflow.state_of.return_value = None
        registry.content.get_workflow.return_value = mock_workflow
        inst = meta.sheet_class(meta, context, registry)
        assert inst.get() == {'workflow': mock_workflow,
                              'workflow_state': None}

    def test_get_cstruct_empty(self, meta, context, registry, mock_workflow):
        mock_workflow.state_of.return_value = None
        mock_workflow.type = 'sample'
        registry.content.get_workflow.return_value = mock_workflow
        inst = meta.sheet_class(meta, context, registry=registry)
        request = testing.DummyRequest(registry=registry)
        assert inst.get_cstruct(request) == {'workflow': 'sample',
                                             'workflow_state': None}

    def test_set_workflow_state(self, meta, context, registry, mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
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

    def test_get_next_states(self, meta, context, registry, mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.get_next_states.return_value = ['announced']
        inst = meta.sheet_class(meta, context, registry=registry)
        request = testing.DummyRequest()
        assert inst.get_next_states(request) == ['announced']
        mock_workflow.get_next_states.assert_called_with(inst.context, request)


class TestSampleWorkflowAssignmentSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.workflow import sample_meta
        return sample_meta

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    def test_create(self, meta, context):
        from adhocracy_core.sheets.workflow import ISample
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        from adhocracy_core.sheets.workflow import WorkflowAssignmentSheet
        from adhocracy_core.sheets.workflow import\
            SampleWorkflowAssignmentSchema
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, WorkflowAssignmentSheet)
        assert inst.meta.isheet == ISample
        assert ISample.isOrExtends(IWorkflowAssignment)
        assert inst.meta.schema_class == SampleWorkflowAssignmentSchema
        assert inst.meta.schema_class.workflow_name == 'sample'
        assert inst.meta.readable is True
        assert inst.meta.editable is True
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, meta, context, registry, mock_workflow):
        mock_workflow.type = 'sample'
        mock_workflow.state_of.return_value = None
        registry.content.get_workflow.return_value = mock_workflow
        inst = meta.sheet_class(meta, context, registry)
        assert inst.get()['participate'] == {}

    def test_get_cstruct_empty(self, meta, context, registry, mock_workflow):
        mock_workflow.type = 'sample'
        registry.content.get_workflow.return_value = mock_workflow
        inst = meta.sheet_class(meta, context, registry=registry)
        request = testing.DummyRequest(registry=registry)
        assert inst.get_cstruct(request)['participate'] ==\
            {'description': 'Start participating!',
             'start_date': '2015-02-14T00:00:00+00:00'}

class TestStandardWorkflowAssignmentSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.workflow import standard_meta
        return standard_meta

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    def test_create(self, meta, context):
        from adhocracy_core.sheets.workflow import IStandard
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        from adhocracy_core.sheets.workflow import WorkflowAssignmentSheet
        from adhocracy_core.sheets.workflow import\
            StandardWorkflowAssignmentSchema
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, WorkflowAssignmentSheet)
        assert inst.meta.isheet == IStandard
        assert IStandard.isOrExtends(IWorkflowAssignment)
        assert inst.meta.schema_class == StandardWorkflowAssignmentSchema
        assert inst.meta.schema_class.workflow_name == 'standard'
        assert inst.meta.readable is True
        assert inst.meta.editable is True
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, meta, context, registry, mock_workflow):
        mock_workflow.type = 'standard'
        mock_workflow.state_of.return_value = None
        registry.content.get_workflow.return_value = mock_workflow
        inst = meta.sheet_class(meta, context, registry)
        assert inst.get()['participate'] == {}

    def test_get_cstruct_empty(self, meta, context, registry, mock_workflow):
        mock_workflow.type = 'standard'
        registry.content.get_workflow.return_value = mock_workflow
        inst = meta.sheet_class(meta, context, registry=registry)
        request = testing.DummyRequest(registry=registry)
        assert inst.get_cstruct(request)['participate'] ==\
            {'description': 'Start participating!',
             'start_date': '2015-02-14T00:00:00+00:00'}

    @mark.usefixtures('integration')
    def test_includeme_register_standard_sheet(self, config):
        from adhocracy_core.sheets.workflow import IStandard
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IStandard)
        inst = get_sheet(context, IStandard)
        assert inst.meta.isheet is IStandard

@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.workflow')


@mark.usefixtures('integration')
def test_includeme_register_sample_sheet(config):
    from adhocracy_core.sheets.workflow import ISample
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=ISample)
    inst = get_sheet(context, ISample)
    assert inst.meta.isheet is ISample


@mark.usefixtures('integration')
def test_includeme_register_generic_workflow_sheet(config):
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IWorkflowAssignment)
    inst = get_sheet(context, IWorkflowAssignment)
    assert inst.meta.isheet is IWorkflowAssignment
