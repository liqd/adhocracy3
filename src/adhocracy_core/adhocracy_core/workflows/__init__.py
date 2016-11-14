"""Finite state machines for resources."""
from colander import Invalid
from pyramid.interfaces import IRequest
from pyramid.registry import Registry
from pyramid.renderers import render
from pyramid.request import Request
from pyramid.threadlocal import get_current_registry
from pyrsistent import freeze
from pyrsistent import PMap
from substanced.workflow import Workflow
from substanced.workflow import WorkflowError
from substanced.util import find_service
from zope.deprecation import deprecated
from zope.interface import implementer
from zope.interface import Interface
from adhocracy_core.authorization import acm_to_acl
from adhocracy_core.authorization import create_fake_god_request
from adhocracy_core.authorization import add_local_roles
from adhocracy_core.authorization import set_acl
from adhocracy_core.exceptions import ConfigurationError
from adhocracy_core.interfaces import DEFAULT_USER_GROUP_NAME
from adhocracy_core.interfaces import IAdhocracyWorkflow
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import search_query
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.workflows.schemas import create_workflow_meta_schema


class ISample(Interface):
    """Sample workflow."""


deprecated('ISample', 'Backward compatible code, remove after migration')


class ACLLocalRolesState(dict):
    """Workflow state setting :term:`acl` and adding :term:`local_roles`."""

    def __init__(self, acl: list=None, local_roles: dict=None, **kw):
        self.acl = acl
        """:term:`acl` set for `context`"""
        self.local_roles = local_roles
        """:class:`adhocracy_core.schema.LocalRoles` added to
        :term:`local_roles` of `context.`
        """

    def __call__(self, context, request, transition, workflow):
        registry = getattr(request, 'registry', None)
        if registry is None:
            registry = get_current_registry(context)
        if self.acl is not None:
            set_acl(context, self.acl, registry)
        if self.local_roles is not None:
            add_local_roles(context,
                            self.local_roles,
                            registry)


@implementer(IAdhocracyWorkflow)
class ACLLocalRolesWorkflow(Workflow):
    """Workflow using `ACLLocalRolesState` to setup states."""

    _state_factory = ACLLocalRolesState

    def get_next_states(self, context, request: IRequest) -> list:
        """Get states you can trigger a transition to."""
        state = self.state_of(context)
        transitions = self.get_transitions(context, request, from_state=state)
        states = [t['to_state'] for t in transitions]
        return list(set(states))

    def update_acl(self, context) -> list:
        """Reset the local permission :term:`acl` for `context`."""
        state = self.state_of(context)
        self._states[state](context, None, None, self)


def update_workflow_state_acls(context: IPool, registry: Registry):
    """Update :term:`acl` of current workflow state for all resources."""
    catalog = find_service(context, 'catalogs')
    query = search_query._replace(interfaces=IWorkflowAssignment)
    resources = catalog.search(query).elements
    for resource in resources:
        workflow = registry.content.get_workflow(resource)
        if workflow is None:
            continue
        workflow.update_acl(resource)


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
        if key in ['initial_state', 'defaults', 'auto_transition',
                   'add_local_role_participant_to_default_group']:
            updated = updated.transform([key], value)
        elif key == 'transitions':
            for transition_name, transition in value.items():
                updated = updated.transform(['transitions', transition_name],
                                            transition)
        elif key == 'states':  # pragma: no branch
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
                     name: str) -> Workflow:
    initial_state = appstruct['initial_state']
    workflow = ACLLocalRolesWorkflow(initial_state=initial_state, type=name)
    if appstruct.get('add_local_role_participant_to_default_group', False):
        group = 'group:' + DEFAULT_USER_GROUP_NAME
        local_roles = {group: {'role:participant'}}
    else:
        local_roles = None
    for name, data in appstruct['states'].items():
        acm = data.get('acm', {})
        acl = acm and acm_to_acl(acm) or []
        workflow.add_state(name, callback=None, acl=acl,
                           local_roles=local_roles)
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
    config.add_workflow('adhocracy_core.workflows:sample.yaml',
                        'sample')
    config.add_workflow('adhocracy_core.workflows:standard.yaml',
                        'standard')
    config.add_workflow('adhocracy_core.workflows:standard_private.yaml',
                        'standard_private')
    config.add_workflow('adhocracy_core.workflows:debate.yaml',
                        'debate')
    config.add_workflow('adhocracy_core.workflows:debate_private.yaml',
                        'debate_private')
    config.add_workflow('adhocracy_core.workflows:badge_assignment.yaml',
                        'badge_assignment')
