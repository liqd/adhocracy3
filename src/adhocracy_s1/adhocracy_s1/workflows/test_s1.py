from pyramid import testing
from pytest import fixture
from pytest import mark
from webtest import TestResponse


@mark.usefixtures('integration')
def test_includeme_add_workflow(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['s1']
    assert isinstance(workflow, AdhocracyACLWorkflow)


@mark.usefixtures('integration')
def test_initiate_and_transition_to_result(registry, context):
    workflow = registry.content.workflows['s1']
    request = testing.DummyRequest()
    assert workflow.state_of(context) is None
    workflow.initialize(context)
    assert workflow.state_of(context) is 'propose'
    workflow.transition_to_state(context, request, 'select')
    assert workflow.state_of(context) is 'select'
    workflow.transition_to_state(context, request, 'result')
    assert workflow.state_of(context) is 'result'
    workflow.transition_to_state(context, request, 'propose')
    assert workflow.state_of(context) is 'propose'


def _post_proposal_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.proposal import IProposal
    resp = app_user.post_resource(path, IProposal, {})
    return resp


def _do_transition_to(app_user, path, state) -> TestResponse:
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    data = {'data': {IWorkflowAssignment.__identifier__:\
                         {'workflow_state': state}}}
    resp = app_user.put(path, data)
    return resp


@mark.functional
class TestS1Workflow:

    def test_propose_participant_creates_proposal(self, app_participant):
        resp = _post_proposal_item(app_participant, path='/s1')
        assert resp.status_code == 200

    def test_propose_participant_can_comment_proposal(self, app_participant2):
        from adhocracy_core.resources.comment import IComment
        assert IComment in app_participant2.get_postable_types(
            '/s1/item_0000000/comments')

    def test_propose_participant_can_rate_proposal(self, app_participant2):
        from adhocracy_core.resources.rate import IRate
        assert IRate in app_participant2.get_postable_types(
            '/s1/item_0000000/rates')

    def test_change_state_to_select(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/s1', 'select')
        assert resp.status_code == 200

    def test_select_participant_cannot_create_proposal(self, app_participant):
        from adhocracy_core.resources.proposal import IProposal
        assert IProposal not in app_participant.get_postable_types('/s1/')

    def test_select_participant_can_comment_proposal(self, app_participant2):
        from adhocracy_core.resources.comment import IComment
        assert IComment in app_participant2.get_postable_types(
            '/s1/item_0000000/comments')

    def test_select_participant_can_rate_proposal(self, app_participant2):
        from adhocracy_core.resources.rate import IRate
        assert IRate in app_participant2.get_postable_types(
            '/s1/item_0000000/rates')

    def test_change_state_to_result(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/s1', 'result')
        assert resp.status_code == 200

    def test_select_participant_cannot_comment_proposal(self, app_participant):
        from adhocracy_core.resources.comment import IComment
        assert IComment not in app_participant.get_postable_types(
            '/s1/item_0000000/comments')

    def test_select_participant_cannot_rate_proposal(self, app_participant):
        from adhocracy_core.resources.rate import IRate
        assert IRate not in app_participant.get_postable_types(
            '/s1/item_0000000/rates')

