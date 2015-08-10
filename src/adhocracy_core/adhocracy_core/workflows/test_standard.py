from pyramid import testing
from pytest import fixture
from pytest import mark

class TestStandardWorkflow:

    def get_acl(self, state, registry):
        from adhocracy_core.schema import ACM
        from adhocracy_core.authorization import acm_to_acl
        from .standard import standard_meta
        acm = ACM().deserialize(standard_meta['states'][state]['acm'])
        acl = acm_to_acl(acm, registry)
        return acl

    def test_draft_moderator_can_view_document(self, registry):
        acl = self.get_acl('draft', registry)
        index_allow = acl.index(('Allow', 'role:moderator', 'view'))
        index_deny = acl.index(('Deny', 'role:participant', 'view'))
        assert index_allow < index_deny

@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration

@mark.usefixtures('integration')
def test_includeme_add_standard_workflow(registry):
    from . import AdhocracyACLWorkflow
    workflow = registry.content.workflows['standard']
    assert isinstance(workflow, AdhocracyACLWorkflow)

@mark.usefixtures('integration')
def test_initiate_and_transition_to_result(registry, context):
    workflow = registry.content.workflows['standard']
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
