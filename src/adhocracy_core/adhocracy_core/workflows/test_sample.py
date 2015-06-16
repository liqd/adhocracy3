from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.rest')
    config.include('adhocracy_core.workflows')


@mark.usefixtures('integration')
def test_includeme_add_sample_workflow(registry):
    from . import AdhocracyACLWorkflow
    workflow = registry.content.workflows['sample']
    assert isinstance(workflow, AdhocracyACLWorkflow)


@mark.usefixtures('integration')
def test_initate_and_transition_to_frozen(registry, context):
    from substanced.util import get_acl
    workflow = registry.content.workflows['sample']
    assert workflow.state_of(context) is None
    workflow.initialize(context)
    assert workflow.state_of(context) is 'participate'
    assert ('Allow', 'role:participant', 'create_proposal') in get_acl(context)
    request = testing.DummyRequest()  # bypass permission check
    workflow.transition_to_state(context, request, 'frozen')
    assert workflow.state_of(context) is 'frozen'
    assert get_acl(context) == []

