"""Finite state machines for resources."""
from colander import Invalid
from pyramid.interfaces import IRequest
from pyramid.registry import Registry
from pyramid.renderers import render
from pyramid.request import Request
from pyrsistent import freeze
from pyrsistent import PMap
from substanced.workflow import ACLWorkflow
from substanced.workflow import WorkflowError
from zope.deprecation import deprecated
from zope.interface import implementer
from zope.interface import Interface

from adhocracy_core.authorization import acm_to_acl
from adhocracy_core.authorization import create_fake_god_request
from adhocracy_core.exceptions import ConfigurationError
from adhocracy_core.interfaces import IAdhocracyWorkflow
from adhocracy_core.workflows.schemas import create_workflow_meta_schema


class ISample(Interface):
    """Sample workflow."""


deprecated('ISample', 'Backward compatible code, remove after migration')


@implementer(IAdhocracyWorkflow)
class AdhocracyACLWorkflow(ACLWorkflow):
    """Workflow that sets the :term:`acl` when entering a State."""

    def get_next_states(self, context, request: IRequest) -> list:
        """Get states you can trigger a transition to."""
        state = self.state_of(context)
        transitions = self.get_transitions(context, request, from_state=state)
        states = [t['to_state'] for t in transitions]
        return list(set(states))


def add_workflow(registry: Registry, workflow_asset: str, name: str):
    """Create and add workflow to registry.

    :param registry: registry to register the workflow and store meta data.
    :param workfow_asset: yaml asset file to import the workflow metadata.
        The data schema is :class:`adhocracy_core.workflows.schemas.Workflow`.
    :param name: identifier for the workflow
    :raises adhocracy_core.exceptions.ConfigurationError: if the validation
        for :term:`cstruct` or the sanity checks in
        class:`substanced.workflow.Workflow` fail.
    """
    cstruct = _get_meta(workflow_asset, registry)
    appstruct = _deserialize_meta(cstruct, name)
    appstruct = _add_defaults(appstruct, registry)
    registry.content.workflows_meta[name] = appstruct
    workflow = _create_workflow(appstruct, name)
    registry.content.workflows[name] = workflow


def _get_meta(workflow_asset: str, registry: Registry) -> dict:
    dummy_request = Request.blank('/')  # pass the local registry in tests
    dummy_request.registry = registry
    cstruct = render(workflow_asset, {}, request=dummy_request)
    return cstruct


def _deserialize_meta(cstruct: dict, name: str) -> PMap:
    schema = create_workflow_meta_schema(cstruct)
    try:
        appstruct = schema.deserialize(cstruct)
    except Invalid as err:
        msg = 'Error add workflow with name {0}: {1}'
        raise ConfigurationError(msg.format(name, str(err.asdict())))
    return freeze(appstruct)


def _add_defaults(appstruct: PMap, registry: Registry) -> PMap:
    """Add values form default workflow to `appstruct`."""
    default_name = appstruct.get('defaults', '')
    if not default_name:
        return appstruct
    updated = registry.content.workflows_meta[default_name]
    for key, value in appstruct.items():
        if key in ['initial_state', 'defaults']:
            updated = updated.transform([key], value)
        elif key == 'transitions':
            for transition_name, transition in value.items():
                updated = updated.transform(['transitions', transition_name],
                                            transition)
        elif key == 'states':
            for state_name, state in value.items():
                for permission in state.get('acm', {}).get('permissions', []):
                    name = permission[0]
                    permissions = \
                        updated['states'][state_name]['acm']['permissions']
                    overwriting = name in [p[0] for p in permissions]
                    if overwriting:
                        updated = updated.transform(
                            ['states', state_name, 'acm', 'permissions',
                             match_permission(updated, state_name, name)],
                            permission)
                    else:
                        updated_permissions = permissions.append(permission)
                        updated = updated.transform(
                            ['states', state_name, 'acm', 'permissions'],
                            updated_permissions)
    return updated


def _create_workflow(appstruct: PMap,
                     name: str) -> ACLWorkflow:
    initial_state = appstruct['initial_state']
    workflow = AdhocracyACLWorkflow(initial_state=initial_state, type=name)
    for name, data in appstruct['states'].items():
        acm = data.get('acm', {})
        acl = acm and acm_to_acl(acm) or []
        workflow.add_state(name, callback=None, acl=acl)
    for name, data in appstruct['transitions'].items():
        workflow.add_transition(name, **data)
    try:
        workflow.check()
    except WorkflowError as err:
        msg = 'Error add workflow with name {0}: {1}'
        raise ConfigurationError(msg.format(name, str(err)))
    return workflow


def add_workflow_directive(config, workflow: str, name: str):
    """Create `add_workflow` pyramid config directive.

    Example usage::

        config.add_workflow('mypackage:myworkflow.yaml', 'myworkflow)
    """
    config.action(('add_workflow', name),
                  add_workflow,
                  args=(config.registry, workflow, name))


def transition_to_states(context, states: [str], registry: Registry,
                         reset=False):
    """Initialize workflow if needed and do transitions to the given states.

    :raises substanced.workflow.WorkflowError: if transition is missing to
    do transitions to `states`.
    """
    request = create_fake_god_request(registry)
    workflow = registry.content.get_workflow(context)
    # TODO: raise if workflow is None
    if not workflow.has_state(context) or reset:
        workflow.initialize(context)
    for state in states:
        workflow.transition_to_state(context, request, state)


def match_permission(acm, state, permission):
    """Create a function matching a permission in an ACM.

    The function can be used as matcher with the `transform`
    function of pyrsistent when transforming an existing ACM to select
    a specific permission to change.

    """
    def matcher(idx):
        return acm['states'][state]['acm']['permissions'][idx][0] == permission
    return matcher


def includeme(config):  # pragma: no cover
    """Include workflows and add 'add_workflow' config directive."""
    config.add_directive('add_workflow', add_workflow_directive)
    config.include('.sample')
    config.include('.standard')
    config.include('.badge_assignment')
    config.include('.standard_private')
    config.include('.debate')
    config.include('.debate_private')
    config.include('.subscriber')
