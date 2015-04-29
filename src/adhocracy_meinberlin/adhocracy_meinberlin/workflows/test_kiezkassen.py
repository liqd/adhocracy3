from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_meinberlin.workflows.kiezkassen')


@mark.usefixtures('integration')
def test_includeme_add_sample_workflow(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['kiezkassen']
    assert isinstance(workflow, AdhocracyACLWorkflow)


@mark.usefixtures('integration')
def test_initiate_and_transition_to_announce(registry, context):
    workflow = registry.content.workflows['kiezkassen']
    request = testing.DummyRequest()
    assert workflow.state_of(context) is None
    workflow.initialize(context)
    assert workflow.state_of(context) is 'draft'
    workflow.transition_to_state(context, request, 'announce')
    assert workflow.state_of(context) is 'announce'
    workflow.transition_to_state(context, request, 'participate')
    assert workflow.state_of(context) is 'participate'
    workflow.transition_to_state(context, request, 'frozen')
    assert workflow.state_of(context) is 'frozen'
    workflow.transition_to_state(context, request, 'result')
    assert workflow.state_of(context) is 'result'
