from unittest.mock import Mock
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
    def resource_meta(self, resource_meta):
        return resource_meta._replace(default_workflow='default',
                                      alternative_workflows=('alternative',))

    @fixture
    def kw(self, registry, mock_workflow, context, resource_meta):
        registry.content.resources_meta[resource_meta.iresource] =\
            resource_meta
        return {'registry': registry,
                'workflow': mock_workflow,
                'creating': None,
                'context': context}

    @fixture
    def inst(self):
        from .workflow import Workflow
        return Workflow()

    def test_create(self, inst, kw, mocker):
        from adhocracy_core.schema import SingleLine
        permission_check = mocker.patch('adhocracy_core.sheets.workflow.'
            'create_deferred_permission_validator').return_value
        inst = inst.bind(**kw)
        assert isinstance(inst, SingleLine)
        assert inst.validator.validators[0].choices == ('',
                                                        'default',
                                                        'alternative')
        assert inst.validator.validators[1] == permission_check.return_value
        assert inst.widget.values == [('default', 'default'),
                                      ('alternative', 'alternative'),
                                      ('', 'No workflow'),
                                      ]

    def test_create_standard_in_alternatives(self, inst, kw, mocker,
                                             resource_meta):
        from adhocracy_core.schema import SingleLine
        kw['creating'] = resource_meta._replace(
            alternative_workflows=('default',))
        permission_check = mocker.patch('adhocracy_core.sheets.workflow.'
                                        'create_deferred_permission_validator').return_value
        inst = inst.bind(**kw)
        assert inst.validator.validators[0].choices == ('',
                                                        'default')
        assert inst.widget.values == [('default', 'default'),
                                      ('', 'No workflow'),
                                      ]

    def test_serialize_empty_without_workflow(self, inst, kw):
        kw['workflow'] = None
        inst = inst.bind(**kw)
        assert inst.serialize() == ''

    def test_serialize_empty_with_workflow(self, inst, kw):
        kw['workflow'].type = 'default'
        inst = inst.bind(**kw)
        assert inst.serialize() == 'default'

    def test_deserialize_default_workflow(self, inst, kw):
        inst = inst.bind(**kw)
        assert inst.deserialize('default') == 'default'

    def test_deserialize_additional_workflows(self, inst, kw):
        inst = inst.bind(**kw)
        assert inst.deserialize('alternative') == 'alternative'

    def test_deserialize_creating_default_workflow(self, inst, kw,
                                                   resource_meta):
        kw['creating'] = resource_meta._replace(
            default_workflow='creating_default')
        inst = inst.bind(**kw)
        assert inst.deserialize('creating_default') == 'creating_default'

    def test_deserialize_raise_if_non_default_or_alternative_workflow(
        self, inst, kw):
        from colander import Invalid
        inst = inst.bind(**kw)
        with raises(Invalid):
            inst.deserialize('other')


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
    assert inst.bind(workflow=None).default == {}


def test_state_data_list():
    from . import workflow
    inst = workflow.StateDataList()
    assert isinstance(inst['data'], workflow.StateData)


def test_workflow_assignment_schema_create():
    import colander
    from adhocracy_core.schema import SingleLine
    from . import workflow
    inst = workflow.WorkflowAssignmentSchema()
    assert isinstance(inst['workflow'], workflow.Workflow)
    assert isinstance(inst['workflow_state'], SingleLine)
    assert inst['workflow_state'].validator == workflow.deferred_state_validator
    assert inst['workflow_state'].missing == colander.drop
    assert inst['workflow_state'].default == workflow.deferred_state_default
    assert isinstance(inst['state_data'], workflow.StateDataList)


class TestDeferredStateValidator:

    @fixture
    def kw(self, context, request_, mock_workflow):
        return {'context': context,
                'request': request_,
                'workflow': mock_workflow,
                'creating': None,
                }

    def call_fut(self, *args):
        from .workflow import deferred_state_validator
        return deferred_state_validator(*args)

    def test_return_empty_list_if_no_workflow(self, node, kw):
        kw['workflow'] = None
        validator = self.call_fut(node, kw)
        assert validator.choices == []

    def test_return_next_states_list_if_workflow(self, node, kw):
        kw['workflow'].get_next_states.return_value = ['state2']
        kw['workflow'].state_of.return_value = 'state1'
        validator = self.call_fut(node, kw)
        assert validator.choices == ['state1', 'state2']
        kw['workflow'].get_next_states.assert_called_with(kw['context'],
                                                          kw['request'])

    def test_return_empty_list_if_creating_but_no_workfow(
        self, node, kw, resource_meta):
        kw['workflow'] = None
        kw['creating'] = resource_meta
        validator = self.call_fut(node, kw)
        assert validator.choices == []

    def test_return_initial_state_if_creating(self, node, kw, resource_meta):
        kw['workflow']._initial_state = 'draft'
        kw['creating'] = resource_meta
        validator = self.call_fut(node, kw)
        assert validator.choices == ['draft']


class TestDeferredStateDefault:

    @fixture
    def kw(self, mock_workflow):
        return {'workflow': mock_workflow}

    def call_fut(self, *args):
        from .workflow import deferred_state_default
        return deferred_state_default(*args)

    def test_return_initial_state(self, node, kw):
        kw['workflow']._initial_state = 'draft'
        assert self.call_fut(node, kw) == 'draft'

    def test_return_empty_string_if_no_workflow(self, node, kw):
        kw['workflow'] = None
        assert self.call_fut(node, kw) == ''


class TestWorkflowAssignmentSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.workflow import workflow_meta
        return workflow_meta

    def test_meta(self, meta):
        from . import workflow
        assert meta.isheet == workflow.IWorkflowAssignment
        assert meta.schema_class == workflow.WorkflowAssignmentSchema
        assert meta.permission_edit == 'do_transition'

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from . import workflow
        inst = meta.sheet_class(meta, context, None)
        assert isinstance(inst, workflow.WorkflowAssignmentSheet)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, meta, context, registry):
        registry.content.get_workflow.return_value = None
        inst = meta.sheet_class(meta, context, registry)
        assert inst.get() == {'workflow': '',
                              'workflow_state': '',
                              'state_data': []}

    def test_get_with_workflow(self, meta, context, registry, mock_workflow):
        inst = meta.sheet_class(meta, context, registry)
        setattr(context, inst._annotation_key, {'workflow': 'sample'})
        registry.content.workflows['sample'] = mock_workflow
        mock_workflow.state_of.return_value = 'draft'
        assert inst.get() == {'workflow': 'sample',
                              'workflow_state': 'draft',
                              'state_data': []}

    def test_get_schema_with_bindings_add_context_workflow(
        self, meta, context, registry, mock_workflow, resource_meta):
        registry.content.resources_meta[resource_meta.iresource] =\
            resource_meta
        inst = meta.sheet_class(meta, context, registry)
        inst._get_data_appstruct = Mock(return_value={'workflow': 'sample'})
        registry.content.workflows['sample'] = mock_workflow
        schema = inst.get_schema_with_bindings()
        assert schema.bindings['workflow'] is mock_workflow

    def test_get_schema_with_bindings_with_creating_add_default_workflow(
        self, meta, context, registry, mock_workflow, resource_meta):
        resource_meta = resource_meta._replace(default_workflow='sample')
        registry.content.workflows['sample'] = mock_workflow
        inst = meta.sheet_class(meta, context, registry, creating=resource_meta)
        schema = inst.get_schema_with_bindings()
        assert schema.bindings['workflow'] is mock_workflow

    def test_set_workflow_state(self, meta, context, registry, mock_workflow,
                                request_):
        inst = meta.sheet_class(meta, context, registry, request=request_)
        mock_workflow._states = {'announced': {}}
        inst._get_data_appstruct = Mock(return_value={'workflow': 'sample'})
        registry.content.workflows['sample'] = mock_workflow
        inst.set({'workflow_state': 'announced'})
        mock_workflow.transition_to_state.assert_called_with(
            context, request_, to_state='announced')

    def test_set_workflow(self, meta, context, registry, mock_workflow,
                          request_):
        inst = meta.sheet_class(meta, context, registry, request=request_)
        registry.content.workflows['sample'] = mock_workflow
        inst.set({'workflow': 'sample'})
        mock_workflow.initialize.assert_called_with(context, request=request_)

    def test_set_workflow_and_state(self, meta, context, registry, request_,
                                    mock_workflow):
        inst = meta.sheet_class(meta, context, registry, request=request_)
        registry.content.workflows['sample'] = mock_workflow
        inst.set({'workflow': 'sample', 'workflow_state': 'announced'})
        mock_workflow.initialize.assert_called_with(context, request=request_)
        assert not mock_workflow.transition_to_state.called

    def test_set_other(self, meta, context, registry, mock_workflow):
        from colander import MappingSchema
        registry.content.get_workflow.return_value = mock_workflow
        inst = meta.sheet_class(meta, context, registry)
        inst.schema = inst.schema.clone()
        inst.schema.add(MappingSchema(name='other'))
        inst.set({'other': {}})
        appstruct = getattr(context, inst._annotation_key)
        assert 'other' in appstruct

    def tet_get_next_states(self, meta, context, registry, mock_workflow):
        registry.content.get_workflow.return_value = mock_workflow
        mock_workflow.get_next_states.return_value = ['announced']
        inst = meta.sheet_class(meta, context, registry)
        request = testing.DummyRequest()
        assert inst.get_next_states(request) == ['announced']
        mock_workflow.get_next_states.assert_called_with(inst.context, request)

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, config):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert config.registry.content.get_sheet(context, meta.isheet)
