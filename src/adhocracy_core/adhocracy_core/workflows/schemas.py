"""Data structures for Workflows."""
from colander import GlobalObject
from colander import Mapping
from colander import MappingSchema
from colander import SchemaNode
from colander import SequenceSchema
from colander import null
from colander import drop
from colander import required
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text
from adhocracy_core.schema import ACM
from adhocracy_core.schema import Roles


class StatesOrder(SequenceSchema):

    """List of state names.

    The first one is the initial state,
    the others are only a hint how to list them
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'default' not in kwargs:  # pragma: no branch
            self.default = []

    state_name = SingleLine()


class WorkflowCallback(SchemaNode):

    """Callable executed if this transition is called or state is entered.

    It needs to provide the following signature::

       context: IResource,
       workflow: IWorkflow=None,
       transition= dict:None,
       request=None
    """

    def schema_type(self):
        return GlobalObject(package=None)

    def serialize(self, appstruct=null):
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

    states_order = StatesOrder(missing=required)
    states = SchemaNode(Mapping(unknown='preserve'),
                        missing=required)
    transitions = SchemaNode(Mapping(unknown='preserve'),
                             missing=required)
    # TODO validate there is only on transition between two states


def create_workflow_meta_schema(data: dict) -> SchemaNode:
    """Create workflowMeta schema and add schemas for states and transitions.

    :dict: data to deserialize/serialize. For every key in states and
           transitions a child schema is added.
    """
    node = WorkflowMeta().clone()
    for name in data['states']:
        schema = StateMeta(name=name, missing=drop)
        node['states'].add(schema)
    for name in data['transitions']:
        schema = TransitionMeta(name=name, missing=drop)
        node['transitions'].add(schema)
    return node
