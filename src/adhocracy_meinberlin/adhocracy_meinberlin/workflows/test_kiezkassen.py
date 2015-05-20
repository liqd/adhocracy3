from pyramid import testing
from pytest import fixture
from pytest import mark
from webtest import TestResponse


@fixture(scope='class')
def app_anonymous(app_anonymous):
    app_anonymous.base_path = '/organisation'
    return app_anonymous

@fixture(scope='class')
def app_participant(app_participant):
    app_participant.base_path = '/organisation'
    return app_participant


@fixture(scope='class')
def app_participant2(app_participant2):
    app_participant2.base_path = '/organisation'
    return app_participant2


@fixture(scope='class')
def app_initiator(app_initiator):
    app_initiator.base_path = '/organisation'
    return app_initiator


@fixture(scope='class')
def app_admin(app_admin):
    app_admin.base_path = '/organisation'
    return app_admin


@fixture(scope='class')
def app_god(app_god):
    app_god.base_path = '/organisation'
    return app_god


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


def _post_proposal_item(app_user, name='', path='') -> TestResponse:
    from adhocracy_meinberlin.resources.kiezkassen import IProposal
    from adhocracy_core.sheets.name import IName
    sheets_cstruct = {IName.__identifier__: {'name': name}}
    resp = app_user.post_resource(path, IProposal, sheets_cstruct)
    return resp


def _post_proposal_item(app_user, name='', path='') -> TestResponse:
    from adhocracy_meinberlin.resources.kiezkassen import IProposal
    from adhocracy_core.sheets.name import IName
    sheets_cstruct = {IName.__identifier__: {'name': name}}
    resp = app_user.post_resource(path, IProposal, sheets_cstruct)
    return resp


def _do_transition_to(app_user, path, state) -> TestResponse:
    from adhocracy_meinberlin.sheets.kiezkassen import IWorkflowAssignment
    data = {'data': {IWorkflowAssignment.__identifier__:\
                         {'workflow_state': state}}}
    resp = app_user.put(path, data)
    return resp


@mark.functional
class TestKiezkassenWorkflow:

    def test_draft_admin_can_view_process(self, app_admin):
        resp = app_admin.get('/kiezkasse')
        assert resp.status_code == 200

    def test_draft_participant_cannot_view_process(self, app_participant):
        resp = app_participant.get('/kiezkasse')
        assert resp.status_code == 403

    def test_draft_participant_cannot_create_proposal(self, app_participant):
        from adhocracy_meinberlin.resources.kiezkassen import IProposal
        assert IProposal not in app_participant.get_postable_types('/kiezkasse')

    def test_change_state_to_announce(self, app_initiator, app_god):
        resp = _do_transition_to(app_initiator, '/kiezkasse', 'announce')
        assert resp.status_code == 200

    def test_announce_participant_can_view_process(self, app_participant):
        resp = app_participant.get('/kiezkasse')
        assert resp.status_code == 200

    def test_participant_cannot_create_proposal(self, app_participant):
        from adhocracy_meinberlin.resources.kiezkassen import IProposal
        assert IProposal not in app_participant.get_postable_types('/kiezkasse')

    def test_change_state_to_participate(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/kiezkasse', 'participate')
        assert resp.status_code == 200

    def test_participate_participant_creates_proposal(self, app_participant):
        resp = _post_proposal_item(app_participant, path='/kiezkasse',
                                   name='proposal')
        assert resp.status_code == 200

    def test_participate_participant_can_comment_proposal(self,
                                                          app_participant):
        from adhocracy_core.resources.comment import IComment
        assert IComment in app_participant.get_postable_types(
            '/kiezkasse/proposal/comments')

    def test_participate_participant_can_rate_proposal(self, app_participant):
        from adhocracy_core.resources.rate import IRate
        assert IRate in app_participant.get_postable_types(
            '/kiezkasse/proposal/rates')

    def test_change_state_to_frozen(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/kiezkasse', 'frozen')
        assert resp.status_code == 200

    def test_frozen_participant_can_view_process(self, app_participant):
        resp = app_participant.get('/kiezkasse')
        assert resp.status_code == 200

    def test_frozen_participant_cannot_comment_other_proposal(self,
                                                              app_participant2):
        from adhocracy_core.resources.comment import IComment
        assert IComment not in app_participant2.get_postable_types(
            '/kiezkasse/proposal/comments')

    def test_frozen_participant_cannot_rate_other_proposal(self,
                                                           app_participant2):
        from adhocracy_core.resources.rate import IRate
        assert IRate not in app_participant2.get_postable_types(
            '/kiezkasse/proposal/rates')

    def test_change_state_to_result(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/kiezkasse', 'result')
        assert resp.status_code == 200

