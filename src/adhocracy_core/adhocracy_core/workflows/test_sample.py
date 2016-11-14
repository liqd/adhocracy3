from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration


@mark.usefixtures('integration')
def test_includeme_add_sample_workflow(registry):
    from . import ACLLocalRolesWorkflow
    workflow = registry.content.workflows['sample']
    assert isinstance(workflow, ACLLocalRolesWorkflow)


@mark.usefixtures('integration')
def test_initate_and_transition_to_frozen(registry, context):
    from adhocracy_core.authorization import get_acl
    workflow = registry.content.workflows['sample']
    assert workflow.state_of(context) == None
    workflow.initialize(context)
    assert workflow.state_of(context) == 'participate'
    assert ('Allow', 'role:participant', 'create_proposal') in get_acl(context)
    assert ('Allow', 'role:participant', 'create_document') in get_acl(context)
    request = testing.DummyRequest()  # bypass permission check
    workflow.transition_to_state(context, request, 'frozen')
    assert workflow.state_of(context) == 'frozen'
    assert get_acl(context) == []

