"""Data structures for Workflows."""
from colander import GlobalObject
from colander import null
from colander import drop
from colander import required
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import MappingType
from adhocracy_core.schema import SchemaNode
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text
from adhocracy_core.schema import ACM
from adhocracy_core.schema import Roles


class WorkflowCallback(SchemaNode):
    """Callable executed if this transition is called or state is entered.

    It needs to provide the following signature::

       context: IResource,
       workflow: IWorkflow=None,
       transition= dict:None,
       request=None
    """

    def schema_type(self):
        """Return schema type."""
        return GlobalObject(package=None)

    def serialize(self, appstruct=null):
        """Serialize."""
        if appstruct in (null, None):
            return None
        return super().serialize(appstruct)

    missing = None
    default = None


class TransitionMeta(MappingSchema):
    """Workflow transition to state."""

    callback = WorkflowCallback()
    from_state = SingleLine(missing=required)
    to_state = SingleLine(missing=required)
    permission = SingleLine(missing='do_transition',
                            default='do_transition')


class StateMeta(MappingSchema):
    """Workflow state."""

    title = SingleLine(missing='')
    description = Text(missing='')
    acm = ACM()
    display_only_to_roles = Roles(missing=[])
    """Hint for the fronted, this is not security related."""


class WorkflowMeta(MappingSchema):
    """Data structure to define a workflow (finite state machine)."""

    initial_state = SingleLine(missing=drop)
    defaults = SingleLine(missing=drop)
    states = SchemaNode(MappingType(unknown='preserve'),
                        missing=drop)
    transitions = SchemaNode(MappingType(unknown='preserve'),
                             missing=drop)
    # TODO validate there is only on transition between two states


def create_workflow_meta_schema(data: dict) -> SchemaNode:
    """Create workflowMeta schema and add schemas for states and transitions.

    :dict: data to deserialize/serialize. For every key in states and
           transitions a child schema is added.
    """
    schema = WorkflowMeta().clone().bind()
    states = data.get('states', {})
    for name in states:
        node = StateMeta(name=name, missing=drop)
        schema['states'].add(node)
    transitions = data.get('transitions', {})
    for name in transitions:
        node = TransitionMeta(name=name, missing=drop)
        schema['transitions'].add(node)
    return schema
