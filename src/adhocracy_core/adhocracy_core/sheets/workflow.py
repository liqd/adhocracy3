"""Sheets to assign workflows to resources and change states."""
from colander import MappingSchema
from colander import deferred
from colander import null
from colander import OneOf
from colander import drop
from pyramid.testing import DummyRequest
from zope.deprecation import deprecated
from zope.interface import implementer

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


class ISample(ISheet):
    """Sheet with the sample workflow."""


deprecated('ISample', 'Backward compatible code, dont use')


class Workflow(AdhocracySchemaNode):
    """Workflow :class:`adhocracy_core.interfaces.IWorkflow`."""

    schema_type = SingleLine.schema_type
    readonly = True
    default = None

    def serialize(self, workflow=null):
        """Serialize the :term:`appstruct` to a :term:`cstruct`."""
        if workflow:
            return workflow.type


@deferred
def deferred_state_validator(node, kw: dict) -> OneOf:
    """Validate workflow state."""
    context = kw['context']
    workflow = kw['workflow']
    request = kw['request']
    if workflow is None:
        next_states = []
    else:
        next_states = workflow.get_next_states(context, request)
    return OneOf(next_states)


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
    end_date = DateTime(missing=None,
                        default=None)


class StateDataList(AdhocracySequenceNode):
    """List of StateData."""

    data = StateData()


class WorkflowAssignmentSchema(MappingSchema):
    """Workflow assignment sheet data structure."""

    workflow = Workflow(missing=drop)
    """Workflow assigned to the sheet context resource.

    Available workflows are defined in :mod:`adhocracy_core.workflows`.
    """

    workflow_state = SingleLine(missing=drop,
                                validator=deferred_state_validator)
    """Workflow state of the sheet context resource.

    Setting this executes a transition to the new state value.
    """

    state_data = StateDataList(missing=drop)
    """Optional List of :class:`StateData`.

    example:

        {'name': 'state1', 'description': 'text', 'start_date': <DateTime>,
         'end_date: <DateTime>}
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

    def get_schema_with_bindings(self):
        schema = self.schema.bind(request=self.request,
                                  registry=self.registry,
                                  context=self.context,
                                  creating=self.creating,
                                  workflow=self._get_workflow()
                                  )
        return schema

    def _get_workflow(self):
        if self.creating:
            name = self.creating.workflow_name
            workflow = self.registry.content.workflows.get(name, None)
        else:
            workflow = self.registry.content.get_workflow(self.context)
        return workflow

    def _store_data(self, appstruct: dict):
        if 'workflow_state' in appstruct:
            self._do_transition_to(appstruct['workflow_state'])
            del appstruct['workflow_state']
        super()._store_data(appstruct)

    def _get_data_appstruct(self) -> dict:
        """Get data appstruct."""
        appstruct = super()._get_data_appstruct()
        workflow = self.registry.content.get_workflow(self.context)
        if workflow:
            appstruct['workflow'] = workflow
            appstruct['workflow_state'] = workflow.state_of(self.context)
        return appstruct

    def _do_transition_to(self, name: str):
        """Do transition to state `name`, don`t check user permissions."""
        workflow = self.get()['workflow']
        request = self.request or DummyRequest()  # ease testing
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
