from pyramid import testing
from pytest import mark
from pytest import fixture
from webtest import TestResponse

# TODO: move _create_proposal to somewhere in backend fixtures as the
# natural dependency ordering is "frontend depends on backend"
from mercator.tests.fixtures.fixturesMercatorProposals1 import _create_proposal
from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposal_batch
from mercator.tests.fixtures.fixturesMercatorProposals1 import update_proposal_batch


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_mercator.workflows')


@mark.usefixtures('integration')
def test_initiate_and_transition_to_announce(registry, context):
    workflow = registry.content.workflows['mercator']
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


@fixture(scope='class')
def app_anonymous(app_anonymous):
    app_anonymous.base_path = '/mercator'
    return app_anonymous

@fixture(scope='class')
def app_participant(app_participant):
    app_participant.base_path = '/mercator'
    return app_participant


@fixture(scope='class')
def app_god(app_god):
    app_god.base_path = '/mercator'
    return app_god

@fixture(scope='class')
def app_initiator(app_initiator):
    app_initiator.base_path = '/mercator'
    return app_initiator

def _post_proposal_item(app_user, path='/',  name='') -> TestResponse:
    from adhocracy_mercator.resources.mercator import IMercatorProposal
    from adhocracy_core.sheets.name import IName
    iresource = IMercatorProposal
    sheets_cstruct = {IName.__identifier__: {'name': name}}
    resp = app_user.post_resource(path, iresource, sheets_cstruct)
    return resp

def _post_proposal_version(app_user, path='/') -> TestResponse:
    from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
    iresource = IMercatorProposalVersion
    resp = app_user.post_resource(path, iresource, {})
    return resp

def _batch_post_full_sample_proposal(app_user) -> TestResponse:
    subrequests = _create_proposal()
    resp = app_user.batch(subrequests)
    return resp

def _do_transition_to(app_user, path, state) -> TestResponse:
    from adhocracy_mercator.sheets.mercator import IWorkflowAssignment
    data = {'data': {IWorkflowAssignment.__identifier__:\
                         {'workflow_state': state}}}
    resp = app_user.put(path, data)
    return resp

@mark.functional
class TestMercatorProposalPermissionsAnonymous:

    def test_cannot_create_proposal_item(self, app_anonymous):
        resp = _post_proposal_item(app_anonymous, path='/', name='proposal1')
        assert resp.status_code == 403

    def test_cannot_create_proposal_per_batch(self, app_anonymous):
        resp = _batch_post_full_sample_proposal(app_anonymous)
        assert resp.status_code == 403

    def test_cannot_create_proposal_per_batch_broken_token(
            self, app_broken_token):
        resp = _batch_post_full_sample_proposal(app_broken_token)
        assert resp.status_code == 400


@mark.functional
class TestMercatorWorkflow:

    ## the state is currently set to 'participate' when creating the mercator process

    # def test_draft_participant_cannot_create_proposal_item(self, app_participant):
    #     from adhocracy_mercator.resources.mercator import IMercatorProposal
    #     assert IMercatorProposal not in app_participant.get_postable_types('/')

    # def test_change_state_to_announce(self, app_initiator):
    #     resp = _do_transition_to(app_initiator, '/', 'announce')
    #     assert resp.status_code == 200

    # def test_announce_participant_cannot_create_proposal_item(self, app_participant):
    #     from adhocracy_mercator.resources.mercator import IMercatorProposal
    #     assert IMercatorProposal not in app_participant.get_postable_types('/')

    # def test_change_state_to_participate(self, app_initiator):
    #     resp = _do_transition_to(app_initiator, '/', 'participate')
    #     assert resp.status_code == 200

    def test_participate_participant_can_create_proposal_item(self, app_participant):
        resp = _post_proposal_item(app_participant, path='/', name='proposal1')
        assert resp.status_code == 200

    def test_participate_can_create_proposal_version(self, app_participant):
        from adhocracy_mercator.resources import mercator
        possible_types = mercator.mercator_proposal_meta.element_types
        postable_types = app_participant.get_postable_types('/proposal1')
        assert set(postable_types) == set(possible_types)

    def test_can_create_and_update_proposal_per_batch(self, app_participant):
        """Create full proposal then do batch request that first
         creates a new subresource Version (IOrganisationInfo) and then
         creates a new proposal Version manually (IUserInfo).

        Fix regression issue #697
        """
        app_participant.batch(create_proposal_batch)
        app_participant.batch(update_proposal_batch)
        assert app_participant.get('/proposal2/VERSION_0000002').json_body['data']['adhocracy_mercator.sheets.mercator.IUserInfo']['personal_name'] == 'pita Updated'
        assert "VERSION_0000002" in  app_participant.get('/proposal2/VERSION_0000002').json_body['data']['adhocracy_mercator.sheets.mercator.IMercatorSubResources']['organization_info']

    def test_cannot_edit_other_users_proposal(self, app_participant,
                                                        app_god):
        _post_proposal_item(app_god, path='/', name='proposal_other')
        _post_proposal_version(app_god, path='/proposal_other')
        postable_types = app_participant.get_postable_types('/proposal_other')
        assert postable_types == []

    def test_non_god_creator_is_set(self, app_participant):
        """Regression test issue #362"""
        from adhocracy_core.sheets.metadata import IMetadata
        resp = app_participant.get('/proposal1')
        creator = resp.json['data'][IMetadata.__identifier__]['creator']
        assert '0000001' in creator

    def test_god_can_create_proposal_item(self, app_god):
        """Regression test issue #362"""
        resp = _post_proposal_item(app_god, path='/', name='god1')
        assert resp.status_code == 200

    def test_god_creator_is_set(self, app_god):
        """Regression test issue #362"""
        from adhocracy_core.sheets.metadata import IMetadata
        resp = app_god.get('/god1')
        creator = resp.json['data'][IMetadata.__identifier__]['creator']
        assert '0000000' in creator
