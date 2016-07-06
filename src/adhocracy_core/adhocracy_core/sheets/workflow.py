"""Sheets to assign workflows to resources and change states."""
from colander import deferred
from colander import OneOf
from colander import drop
from colander import All
from deform.widget import SelectWidget
from deform.widget import Widget
from pyramid.testing import DummyRequest
from zope.deprecation import deprecated
from zope.interface import implementer

from adhocracy_core.interfaces import ISheet
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import Text
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import SequenceSchema
from adhocracy_core.schema import SchemaNode
from adhocracy_core.schema import create_deferred_permission_validator
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import AnnotationRessourceSheet
from adhocracy_core.utils import get_iresource
from adhocracy_core.interfaces import IResourceSheet
from adhocracy_core.interfaces import IWorkflow


class ISample(ISheet):
    """Sheet with the sample workflow."""


deprecated('ISample', 'Backward compatible code, dont use')


@deferred
def deferred_state_validator(node, kw: dict) -> OneOf:
    """Validate workflow state."""
    context = kw['context']
    workflow = kw['workflow']
    request = kw['request']
    creating = kw['creating']
    if workflow is None:
        allowed = []
    elif creating:
        allowed = [workflow._initial_state]
    else:
        nexts = workflow.get_next_states(context, request)
        current = workflow.state_of(context)
        allowed = [current] + nexts
    return OneOf(allowed)


@deferred
def deferred_state_default(node, kw: dict) -> str:
    """Return initial workflow state."""
    workflow = kw['workflow']
    initial_state = workflow and workflow._initial_state or ''
    return initial_state


@deferred
def deferred_state_widget(node, kw: dict) -> Widget:
    """Workflow state widget."""
    validator = deferred_state_validator(node, kw)
    states = [(x, x) for x in validator.choices]
    return SelectWidget(values=states)


class StateName(SingleLine):
    """Workflow state name.

    Possible values are set by the given `workflow` binding.
    """

    @deferred
    def validator(self, kw: dict):
        """Validator."""
        workflow = kw['workflow']
        if workflow is None:
            states = []
        else:
            states = workflow._states.keys()
        return OneOf(states)

    @deferred
    def widget(self, kw: dict) -> Widget:
        states = [(x, x) for x in self.validator.choices]
        return SelectWidget(values=states)


class StateData(MappingSchema):
    """Resource specific data for a workflow state."""

    missing = drop

    @deferred
    def default(self, kw):
        return {}

    name = StateName()
    description = Text(missing='',
                       default='')
    start_date = DateTime(missing=None,
                          default=None)


class StateDataList(SequenceSchema):
    """List of StateData."""

    data = StateData()


def deferred_workflow_validator(node: SchemaNode, kw: dict) -> callable:
    """Deferred workflow name validator."""
    context = kw['context']
    registry = kw['registry']
    creating = kw['creating']
    if creating:
        meta = creating
    else:
        iresource = get_iresource(context)
        meta = registry.content.resources_meta[iresource]
    if meta.default_workflow in meta.alternative_workflows:
        workflows = ('',) + meta.alternative_workflows
    else:
        workflows = ('', meta.default_workflow) + meta.alternative_workflows
    return OneOf(workflows)


class Workflow(SingleLine):
    """SchemaNode for workflow types.

    Default value requires the schema binding `workflow`.
    """

    @deferred
    def default(node: MappingSchema, kw: dict) -> IWorkflow:
        workflow = kw['workflow']
        return workflow and workflow.type or ''

    @deferred
    def validator(node: MappingSchema, kw: dict):
        return All(deferred_workflow_validator(node, kw),
                   create_deferred_permission_validator('edit_workflow')(node,
                                                                         kw),
                   )

    @deferred
    def widget(node: MappingSchema, kw: dict) -> SelectWidget:
        """Return widget to select the wanted workflow."""
        valid_names = deferred_workflow_validator(node, kw).choices
        choices = [(w, w) for w in valid_names]
        choices.remove(('', ''))
        choices.append(('', 'No workflow'))
        return SelectWidget(values=choices)


class WorkflowAssignmentSchema(MappingSchema):
    """Workflow assignment sheet data structure."""

    workflow = Workflow(missing=drop)
    """Workflow assigned to the sheet context resource.

    Available workflows are defined in :mod:`adhocracy_core.workflows`.
    """

    workflow_state = SingleLine(missing=drop,
                                default=deferred_state_default,
                                validator=deferred_state_validator,
                                widget=deferred_state_widget,
                                )
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

    It allows to view and modify the workflow state of `context`.
    If the you set a new workflow state a transition to this state is executed.

    The workflow of `context` is only found, if the :term:`resource_type`
    metadata of `context` has a valid 'workflow` entry.
    """

    def _get_basic_bindings(self) -> dict:
        bindings = super()._get_basic_bindings()
        workflow = self._get_workflow()
        bindings['workflow'] = workflow
        return bindings

    def _get_workflow(self) -> IWorkflow:
        if self.creating:
            name = self.creating.default_workflow
        else:
            name = self._get_data_appstruct().get('workflow')
        workflow = self.registry.content.workflows.get(name, None)
        return workflow

    def _store_data(self, appstruct: dict, initialize_workflow=True):
        if 'workflow' in appstruct and 'workflow_state' in appstruct:
            del appstruct['workflow_state']  # we cannot change both
        if 'workflow' in appstruct and initialize_workflow:
            self._initialize(appstruct['workflow'])
        elif 'workflow_state' in appstruct:
            self._do_transition_to(appstruct['workflow_state'])
            del appstruct['workflow_state']
        super()._store_data(appstruct)

    def _initialize(self, name: str):
        if name != '':
            workflow = self.registry.content.workflows[name]
            workflow.initialize(self.context, request=self.request)

    def _get_data_appstruct(self) -> dict:
        """Get data appstruct."""
        appstruct = super()._get_data_appstruct()
        if 'workflow' in appstruct:
            name = appstruct['workflow']
            if name:
                workflow = self.registry.content.workflows[name]
                appstruct['workflow_state'] = workflow.state_of(self.context)
        return appstruct

    def _do_transition_to(self, name: str):
        """Do transition to state `name`, don`t check user permissions."""
        request = self.request or DummyRequest()  # ease testing
        workflow = self._get_workflow()
        workflow.transition_to_state(self.context, request, to_state=name)


workflow_meta = sheet_meta._replace(
    isheet=IWorkflowAssignment,
    schema_class=WorkflowAssignmentSchema,
    sheet_class=WorkflowAssignmentSheet,
    permission_edit='do_transition'
)


def includeme(config):
    """Add sheet."""
    add_sheet_to_registry(workflow_meta, config.registry)
