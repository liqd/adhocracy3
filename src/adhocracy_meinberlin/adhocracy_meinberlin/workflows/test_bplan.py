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
    config.include('adhocracy_meinberlin.workflows.bplan')


@mark.usefixtures('integration')
def test_includeme_add_sample_workflow(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['bplan']
    assert isinstance(workflow, AdhocracyACLWorkflow)


def _post_proposal_item(app_user, name='', path='') -> TestResponse:
    from adhocracy_meinberlin.resources.bplan import IProposal
    from adhocracy_core.sheets.name import IName
    sheets_cstruct = {IName.__identifier__: {'name': name}}
    resp = app_user.post_resource(path, IProposal, sheets_cstruct)
    return resp


def _post_proposal_item(app_user, name='', path='') -> TestResponse:
    from adhocracy_meinberlin.resources.bplan import IProposal
    from adhocracy_core.sheets.name import IName
    sheets_cstruct = {IName.__identifier__: {'name': name}}
    resp = app_user.post_resource(path, IProposal, sheets_cstruct)
    return resp


def _do_transition_to(app_user, path, state) -> TestResponse:
    from adhocracy_meinberlin.sheets.bplan import IWorkflowAssignment
    data = {'data': {IWorkflowAssignment.__identifier__:\
                         {'workflow_state': state}}}
    resp = app_user.put(path, data)
    return resp


@mark.functional
class TestBPlanWorkflow:

    def test_draft_admin_can_view_process(self, app_admin):
        resp = app_admin.get('/bplan')
        assert resp.status_code == 200

    def test_draft_initiator_can_view_process(self, app_initiator):
        resp = app_initiator.get(path='/bplan')
        assert resp.status_code == 200

    def test_draft_participant_cannot_view_process(self, app_participant):
        resp = app_participant.get('/bplan')
        assert resp.status_code == 403

    def test_draft_participant_cannot_create_proposal(self, app_participant):
        from adhocracy_meinberlin.resources.bplan import IProposal
        assert IProposal not in app_participant.get_postable_types('/bplan')

    def test_change_state_to_announce(self, app_initiator, app_god):
        resp = _do_transition_to(app_initiator, '/bplan', 'announce')
        assert resp.status_code == 200

    def test_announce_participant_can_view_process(self, app_participant):
        resp = app_participant.get('/bplan')
        assert resp.status_code == 200

    def test_participant_cannot_create_proposal(self, app_participant):
        from adhocracy_meinberlin.resources.bplan import IProposal
        assert IProposal not in app_participant.get_postable_types('/bplan')

    def test_change_state_to_participate(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/bplan', 'participate')
        assert resp.status_code == 200

    def test_participate_participant_creates_proposal(self, app_participant):
        resp = _post_proposal_item(app_participant, path='/bplan',
                                   name='proposal')
        assert resp.status_code == 200

    def test_participate_participant_cannot_edit_his_own_proposal(self, app_participant):
        from adhocracy_meinberlin.resources.bplan import IProposalVersion
        assert IProposalVersion not in app_participant.get_postable_types(
            '/bplan/proposal')

    def test_participate_participant_can_view_his_own_proposal(self,
                                                               app_participant):
        resp = app_participant.get(path='/bplan/proposal')
        assert resp.status_code == 200

    def test_participate_participant_cannot_view_proposal(self, app_participant2):
        resp = app_participant2.get(path='/bplan/proposal')
        assert resp.status_code == 404

    def test_participate_initiator_can_view_proposal(self, app_initiator):
        resp = app_initiator.get(path='/bplan/proposal')
        assert resp.status_code == 200

    def test_change_state_to_frozen(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/bplan', 'frozen')
        assert resp.status_code == 200

    def test_frozen_participant_cannot_create_proposal(self, app_participant):
        from adhocracy_meinberlin.resources.bplan import IProposal
        assert IProposal not in app_participant.get_postable_types('/bplan')

    def test_frozen_initiator_can_view_proposal(self, app_participant2):
        resp = app_participant2.get(path='/bplan/proposal')
        assert resp.status_code == 200

    def test_frozen_participant_can_view_process(self, app_participant):
        resp = app_participant.get('/bplan')
        assert resp.status_code == 200

    def test_frozen_participant_cannot_view_proposal(self, app_participant2):
        resp = app_participant2.get('/bplan/proposal')
        assert resp.status_code == 404
