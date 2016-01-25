from pyramid import testing
from pytest import fixture
from pytest import mark
from webtest import TestResponse

from adhocracy_core.utils.testing import do_transition_to

@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration

@mark.usefixtures('integration')
def test_includeme(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['debate']
    assert isinstance(workflow, AdhocracyACLWorkflow)


@mark.usefixtures('integration')
def test_initiate_and_transition_to_announce(registry, context):
    workflow = registry.content.workflows['debate']
    request = testing.DummyRequest()
    assert workflow.state_of(context) is None
    workflow.initialize(context)
    assert workflow.state_of(context) is 'draft'
    workflow.transition_to_state(context, request, 'announce')
    assert workflow.state_of(context) is 'announce'
    workflow.transition_to_state(context, request, 'participate')
    assert workflow.state_of(context) is 'participate'
    workflow.transition_to_state(context, request, 'evaluate')
    assert workflow.state_of(context) is 'evaluate'
    workflow.transition_to_state(context, request, 'result')
    assert workflow.state_of(context) is 'result'
    workflow.transition_to_state(context, request, 'closed')
    assert workflow.state_of(context) is 'closed'
