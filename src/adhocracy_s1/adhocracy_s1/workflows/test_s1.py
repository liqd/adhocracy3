from pyramid import testing
from pytest import fixture
from pytest import mark
from webtest import TestResponse


class TestChangeChildrenToVotable:

    @fixture
    def registry(self, registry_with_content, mock_workflow):
        registry_with_content.content.get_workflow.return_value = mock_workflow
        return registry_with_content

    def call_fut(self, *args, **kwargs):
        from .s1 import change_children_to_voteable
        return change_children_to_voteable(*args, **kwargs)

    def test_ignore_if_no_workflow(self, context, request_, registry):
        context['child'] = testing.DummyResource()
        registry.content.get_workflow.return_value = None
        self.call_fut(context, request_)

    def test_ignore_if_state_is_not_propose(self, context, request_, registry,
                                            mock_workflow):
        context['child'] = testing.DummyResource()
        mock_workflow.state_of.return_value = ''
        self.call_fut(context, request_)
        assert not mock_workflow.transition_to_state.called

    def test_change_children_to_votable(self, context, request_, registry,
                                        mock_workflow):
        context['child'] = testing.DummyResource()
        mock_workflow.state_of.return_value = 'proposed'
        self.call_fut(context, request_)
        mock_workflow.transition_to_state.assert_called_with(context['child'],
                                                             request_, 'voteable')


class TestChangeChildrenToRejected:

    @fixture
    def registry(self, registry_with_content, mock_workflow):
        registry_with_content.content.get_workflow.return_value = mock_workflow
        return registry_with_content

    def call_fut(self, *args, **kwargs):
        from .s1 import change_children_to_rejected
        return change_children_to_rejected(*args, **kwargs)

    def test_ignore_if_no_workflow(self, context, request_, registry):
        context['child'] = testing.DummyResource()
        registry.content.get_workflow.return_value = None
        self.call_fut(context, request_)

    def test_ignore_if_state_is_not_voteable(self, context, request_, registry,
                                             mock_workflow):
        context['child'] = testing.DummyResource()
        mock_workflow.state_of.return_value = ''
        self.call_fut(context, request_)
        assert not mock_workflow.transition_to_state.called

    def test_change_children_to_rejected(self, context, request_, registry,
                                         mock_workflow):
        context['child'] = testing.DummyResource()
        mock_workflow.state_of.return_value = 'voteable'
        self.call_fut(context, request_)
        mock_workflow.transition_to_state.assert_called_with(context['child'],
                                                             request_, 'rejected')


@mark.usefixtures('integration')
def test_s1_includeme_add_workflow(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['s1']
    assert isinstance(workflow, AdhocracyACLWorkflow)


@mark.usefixtures('integration')
def test_s1_initiate_and_transition_to_result(registry, context, request_):
    workflow = registry.content.workflows['s1']
    request = testing.DummyRequest()
    workflow.initialize(context)
    assert workflow.state_of(context) is 'propose'
    workflow.transition_to_state(context, request, 'select')
    workflow.transition_to_state(context, request, 'result')
    workflow.transition_to_state(context, request, 'propose')


def _post_proposal_item(app_user, path='') -> TestResponse:
    from adhocracy_s1.resources.s1 import IProposal
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

    def test_propose_participant_can_create_proposal(self, app_participant):
        resp = _post_proposal_item(app_participant, path='/s1')
        assert 'proposal_0000000' in resp.json['path']

    def test_propose_proposal_has_state_propose(self, app_participant):
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        resp = app_participant.get('/s1/proposal_0000000')
        assert resp.json['data'][IWorkflowAssignment.__identifier__]['workflow_state'] == 'proposed'

    def test_propose_participant_can_comment_proposal(self, app_participant2):
        from adhocracy_core.resources.comment import IComment
        assert IComment in app_participant2.get_postable_types(
            '/s1/proposal_0000000/comments')

    def test_propose_participant_can_rate_proposal(self, app_participant2):
        from adhocracy_core.resources.rate import IRate
        assert IRate in app_participant2.get_postable_types(
            '/s1/proposal_0000000/rates')

    def test_change_state_to_select(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/s1', 'select')
        assert resp.status_code == 200

    def test_select_proposal_has_state_votable(self, app_participant):
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        resp = app_participant.get('/s1/proposal_0000000')
        assert resp.json['data'][IWorkflowAssignment.__identifier__]['workflow_state'] == 'voteable'

    def test_select_participant_can_create_proposal(self, app_participant):
        resp = _post_proposal_item(app_participant, path='/s1')
        assert 'proposal_0000001' in resp.json['path']

    def test_select_participant_can_comment_proposal(self, app_participant2):
        from adhocracy_core.resources.comment import IComment
        assert IComment in app_participant2.get_postable_types(
            '/s1/proposal_0000000/comments')

    def test_select_participant_can_rate_proposal(self, app_participant2):
        from adhocracy_core.resources.rate import IRate
        assert IRate in app_participant2.get_postable_types(
            '/s1/proposal_0000000/rates')

    def test_change_state_to_result(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/s1', 'result')
        assert resp.status_code == 200

    def test_result_old_proposal_has_state_rejected(self, app_participant):
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        resp = app_participant.get('/s1/proposal_0000000')
        assert resp.json['data'][IWorkflowAssignment.__identifier__]['workflow_state'] == 'rejected'

    def test_result_participant_cannot_comment_old_proposal(self, app_participant2):
        from adhocracy_core.resources.comment import IComment
        assert IComment not in app_participant2.get_postable_types(
            '/s1/proposal_0000002/comments')

    def test_result_participant_cannot_rate_old_proposal(self, app_participant2):
        from adhocracy_core.resources.rate import IRate
        assert IRate not in app_participant2.get_postable_types(
            '/s1/proposal_0000002/rates')

    def test_result_participant_can_create_proposal(self, app_participant):
        resp = _post_proposal_item(app_participant, path='/s1')
        assert 'proposal_0000002' in resp.json['path']

    def test_result_participant_can_comment_proposal(self, app_participant2):
        from adhocracy_core.resources.comment import IComment
        assert IComment in app_participant2.get_postable_types(
            '/s1/proposal_0000002/comments')

    def test_result_participant_can_rate_proposal(self, app_participant2):
        from adhocracy_core.resources.rate import IRate
        assert IRate in app_participant2.get_postable_types(
            '/s1/proposal_0000002/rates')


@mark.usefixtures('integration')
def test_s1_content_includeme_add_workflow(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['s1_content']
    assert isinstance(workflow, AdhocracyACLWorkflow)


@mark.usefixtures('integration')
def test_s1_content_initiate_and_transition_to_selected(registry, context,
                                                        request_):
    workflow = registry.content.workflows['s1_content']
    workflow.initialize(context)
    assert workflow.state_of(context) is 'proposed'
    workflow.transition_to_state(context, request_, 'voteable')
    workflow.transition_to_state(context, request_, 'selected')


