"""Assign workflows to resources and change states."""
from datetime import datetime
from colander import Invalid
from colander import MappingSchema
from colander import SchemaType
from colander import deferred
from colander import null
from colander import OneOf
from pyramid.testing import DummyRequest
from pyramid.interfaces import IRequest
from substanced.workflow import IWorkflow
from zope.interface import implementer

from adhocracy_core.exceptions import RuntimeConfigurationError
from adhocracy_core.interfaces import ISheet
from adhocracy_core.schema import AdhocracySchemaNode
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import Text
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_metadata_defaults
from adhocracy_core.sheets import AnnotationStorageSheet
from adhocracy_core.interfaces import IPropertySheet


class WorkflowType(SchemaType):

    """A workflow object.

    Example value: 'sample'
    """

    def serialize(self, node, value) -> str:
        """Serialize :class:`substanced.workflow.IWorkflow' to type name."""
        if value in (null, None):
            return ''
        return value.type

    def deserialize(self, node, value) -> IWorkflow:
        """Serialize name to :class:`substanced.workflow.IWorkflow'."""
        if value == '':
            return None
        registry = node.bindings['registry']
        try:
            workflow = registry.content.get_workflow(value)
        except RuntimeConfigurationError:
            msg = 'This workflow name does not exists: {0}'.format(str(value))
            raise Invalid(node, msg=msg, value=value)
        return workflow


class Workflow(AdhocracySchemaNode):

    schema_type = WorkflowType
    readonly = True
    default_workflow_name = ''

    @deferred
    def default(self, kw):
        registry = kw['registry']
        workflow = registry.content.get_workflow(self.default_workflow_name)
        return workflow


class StateType(SchemaType):

    """A workflow state object.

    Example value: 'draft'
    """

    def serialize(self, node, value) -> str:
        """Serialize workflow state."""
        if value is null:
            return None
        return value

    def deserialize(self, node, value) -> IWorkflow:
        """Deserialize workflow state."""
        return value


class State(AdhocracySchemaNode):

    workflow_name = ''
    schema_type = StateType

    @deferred
    def default(self, kw: dict) -> str:
        registry = kw['registry']
        context = kw['context']
        if self.workflow_name == '':
            return None
        workflow = registry.content.get_workflow(self.workflow_name)
        state = workflow.state_of(context)
        return state

    @deferred
    def validator(self, kw: dict):
        request = kw.get('request', None)
        if request is None:
            return
        context = kw['context']
        workflow = request.registry.content.get_workflow(self.workflow_name)
        next_states = workflow.get_next_states(context, request)

        def validate_next_states(node, value):
            return OneOf(next_states)(node, value)
        return validate_next_states


class StateAssignment(MappingSchema):

    """Resource specific data for a workflow state."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'default' not in kwargs:  # pragma: no branch
            self.default = {}

    description = Text(missing='',
                       default='Soon you can participate')
    start_date = DateTime(missing=None,
                          default=datetime(2015, 2, 14))


class WorkflowAssignmentSchema(MappingSchema):

    """Assign workflow to resource type, optional add StateAssignment data."""

    workflow_name = 'WRONG'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['workflow'].default_workflow_name = self.workflow_name
        self['workflow_state'].workflow_name = self.workflow_name

    workflow = Workflow()
    """Workflow assigned to the sheet context resource.

    This is readonly, the workflow is set by the `workflow_name` attribute.
    Available workflows are defined in :mod:`adhocracy_core.workflows`.
    """

    workflow_state = State()
    """Workflow state of the sheet context resource.

    Setting this excecutes a transition to the new state value.
    """


class IWorkflowAssignment(ISheet):

    """Market interface for the WorkflowAssignments sheets."""


@implementer(IPropertySheet)
class WorkflowAssignmentSheet(AnnotationStorageSheet):

    """Generic sheet for IWorkflowAssignment isheets."""

    def get_next_states(self, request: IRequest) -> [str]:
        """Get possible transition to states.

        :param request: check user permissions
        """
        workflow = self.get()['workflow']
        states = workflow.get_next_states(self.context, request)
        return states

    def _store_data(self, appstruct):
        if 'workflow_state' in appstruct:
            self._set_state(appstruct['workflow_state'])
            del appstruct['workflow_state']
        super()._store_data(appstruct)

    def _set_state(self, name: str):
        """Do transition to state `name`, don`t check user permissions."""
        workflow = self.get()['workflow']
        request = DummyRequest()  # bypass permission check
        workflow.transition_to_state(self.context, request, to_state=name)


workflow_meta = sheet_metadata_defaults._replace(
    isheet=IWorkflowAssignment,
    schema_class=WorkflowAssignmentSchema,
    sheet_class=WorkflowAssignmentSheet,
)


class ISample(IWorkflowAssignment):

    """Assign workflow to resource type, optional add StateAssignment data."""


class SampleWorkflowAssignmentSchema(WorkflowAssignmentSchema):

    workflow_name = 'sample'

    announced = StateAssignment()
    """Optional data related to a workflow state.

    The field name has to match an existing state name.
    """

sample_meta = workflow_meta._replace(
    isheet=ISample,
    schema_class=SampleWorkflowAssignmentSchema,
)


def includeme(config):
    """Add sheet."""
    add_sheet_to_registry(sample_meta, config.registry)
    add_sheet_to_registry(workflow_meta, config.registry)
