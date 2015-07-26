"""Sheets to assign workflows to resources and change states."""
from colander import MappingSchema
from colander import deferred
from colander import null
from colander import OneOf
from colander import drop
from pyramid.testing import DummyRequest
from pyramid.threadlocal import get_current_request
from substanced.workflow import IWorkflow
from zope.interface import implementer
from zope.deprecation import deprecated

from adhocracy_core.exceptions import RuntimeConfigurationError
from adhocracy_core.interfaces import ISheet
from adhocracy_core.schema import AdhocracySchemaNode
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import Text
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import AdhocracySequenceNode
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import AnnotationRessourceSheet
from adhocracy_core.interfaces import IResourceSheet


class Workflow(AdhocracySchemaNode):

    """Workflow :class:`adhocracy_core.interfaces.IWorkflow`.

    This schema node is readonly. The value is given by the node binding
    `workflow`.
    """

    schema_type = SingleLine.schema_type
    readonly = True

    @deferred
    def default(self, kw: dict) -> IWorkflow:
        return kw.get('workflow', None)

    def serialize(self, appstruct=null):
        """ Serialize the :term:`appstruct` to a :term:`cstruct`."""
        workflow = self.bindings['workflow']
        if workflow is None:
            return ''
        return workflow.type


class State(SingleLine):

    """Workflow state of `context` of the given `workflow` binding."""

    missing = drop

    @deferred
    def default(self, kw: dict) -> str:
        """Return default value."""
        workflow = kw.get('workflow', None)
        if workflow is None:
            return ''
        context = kw['context']
        state = workflow.state_of(context)
        if state is None:
            state = ''
        return state

    @deferred
    def validator(self, kw: dict):
        """Validator."""
        request = kw.get('request', None)
        if request is None:
            return
        workflow = kw.get('workflow', None)
        if workflow is None:
            next_states = []
        else:
            context = kw['context']
            next_states = workflow.get_next_states(context, request)

        def validate_next_states(node, value):
            return OneOf(next_states)(node, value)
        return validate_next_states


class StateName(SingleLine):

    """Workflow state name.

    Possible values are set by the given `workflow` binding.
    """

    @deferred
    def validator(self, kw: dict):
        """Validator."""
        workflow = kw.get('workflow', None)
        if workflow is None:
            states = []
        else:
            states = workflow._states.keys()  # TODO don't use private attr

        def validate_state_name(node, value):
            return OneOf(states)(node, value)
        return validate_state_name


class StateData(MappingSchema):

    """Resource specific data for a workflow state."""

    missing = drop
    default = None

    name = StateName()
    description = Text(missing='',
                       default='')
    start_date = DateTime(missing=None,
                          default=None)


class StateDataList(AdhocracySequenceNode):

    data = StateData()


class WorkflowAssignmentSchema(MappingSchema):

    """Workflow assignment sheet data structure."""

    workflow = Workflow(missing=drop)
    """Workflow assigned to the sheet context resource.

    This is readonly, the workflow is set by the `workflow` binding.
    Available workflows are defined in :mod:`adhocracy_core.workflows`.
    """

    workflow_state = State(missing=drop)
    """Workflow state of the sheet context resource.

    Setting this executes a transition to the new state value.
    """

    state_data = StateDataList(missing=drop)
    """Optional List of :class:`StateData`.

    example:

        {'name': 'state1', 'description': 'text', 'start_date': <DateTime>}
    """


class IWorkflowAssignment(ISheet):

    """Market interface for the workflow assignment sheet."""


@implementer(IResourceSheet)
class WorkflowAssignmentSheet(AnnotationRessourceSheet):

    """Sheet class for workflow assignment sheets.

    It allows to view and modifiy the workflow state of `context`.
    If the you set a new workflow state a transition to this state is executed.

    The workflow of `context` is only found, if the :term:`resource_type`
    metadata of `context` has a valid 'workflow` entry.

    The sheet schema has to be a sup type of
    :class:`adhocracy_core.sheets.workflow.WorkflowAssignmentSchema`,
    the isheet a subclass of
    :class:`adhocracy_core.sheets.workflow.IWorkflowAssignment`.
    """

    def __init__(self, meta, context, registry=None):
        """Initialize self."""
        super().__init__(meta, context, registry)
        error_msg = '{0} is not a sub type of {1}.'
        if not meta.isheet.isOrExtends(IWorkflowAssignment):
            msg = error_msg.format(str(meta.isheet), str(IWorkflowAssignment))
            raise RuntimeConfigurationError(msg)
        if not isinstance(self.schema, WorkflowAssignmentSchema):
            msg = error_msg.format(str(meta.schema_class),
                                   str(WorkflowAssignmentSchema))
            raise RuntimeConfigurationError(msg)

    def _get_default_appstruct(self) -> dict:
        workflow = self.registry.content.get_workflow(self.context)
        schema = self.schema.bind(context=self.context,
                                  registry=self.registry,
                                  workflow=workflow)
        items = [(n.name, n.default) for n in schema]
        return dict(items)

    def _get_schema_for_cstruct(self, request, params: dict):
        workflow = self.registry.content.get_workflow(self.context)
        schema = self.schema.bind(context=self.context,
                                  registry=self.registry,
                                  workflow=workflow,
                                  request=request)
        return schema

    def _store_data(self, appstruct: dict):
        if 'workflow_state' in appstruct:
            self._set_state(appstruct['workflow_state'])
            del appstruct['workflow_state']
        super()._store_data(appstruct)

    def _set_state(self, name: str):
        """Do transition to state `name`, don`t check user permissions."""
        workflow = self.get()['workflow']
        request = get_current_request() or DummyRequest()  # ease testing
        workflow.transition_to_state(self.context, request, to_state=name)


workflow_meta = sheet_meta._replace(
    isheet=IWorkflowAssignment,
    schema_class=WorkflowAssignmentSchema,
    sheet_class=WorkflowAssignmentSheet,
    permission_edit='do_transition'
)


class ISample(IWorkflowAssignment):

    """Marker interface for the sample workflow assignment sheet."""


deprecated('ISample',
           'Backward compatible code use process IWorkflowAssignment instead')


class IStandard(IWorkflowAssignment):

    """Marker interface for the standard workflow assignment sheet."""


deprecated('IStandard',
           'Backward compatible code use process IWorkflowAssignment instead')


def includeme(config):
    """Add sheet."""
    add_sheet_to_registry(workflow_meta, config.registry)
