from pyramid import testing
from pytest import mark
from pytest import fixture
from webtest import TestResponse

# TODO: move _create_proposal to somewhere in backend fixtures as the
# natural dependency ordering is "frontend depends on backend"
from mercator.tests.fixtures.fixturesMercatorProposals1 import _create_proposal
from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposal_batch
from mercator.tests.fixtures.fixturesMercatorProposals1 import update_proposal_batch
from adhocracy_core.testing import do_transition_to


@mark.usefixtures('integration')
def test_initiate_and_transition_to_announce(registry, context):
    workflow = registry.content.workflows['mercator']
    request = testing.DummyRequest()
    assert workflow.state_of(context) is None
    workflow.initialize(context)
    assert workflow.state_of(context) == 'draft'
    workflow.transition_to_state(context, request, 'announce')
    assert workflow.state_of(context) == 'announce'
    workflow.transition_to_state(context, request, 'participate')
    assert workflow.state_of(context) == 'participate'
    workflow.transition_to_state(context, request, 'evaluate')
    assert workflow.state_of(context) == 'evaluate'
    workflow.transition_to_state(context, request, 'result')
    assert workflow.state_of(context) == 'result'


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


def _post_proposal_item(app_user, path='/') -> TestResponse:
    from adhocracy_mercator.resources.mercator import IMercatorProposal
    resp = app_user.post_resource(path, IMercatorProposal,   {})
    return resp


def _post_proposal_version(app_user, path='/') -> TestResponse:
    from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
    iresource = IMercatorProposalVersion
    resp = app_user.post_resource(path, iresource, {})
    return resp


def _post_document_item(app_user, path='/') -> TestResponse:
    from adhocracy_core.resources.document import IDocument
    resp = app_user.post_resource(path, IDocument, {})
    return resp


def _post_document_version(app_user, path='/') -> TestResponse:
    from adhocracy_core.resources.document import IDocumentVersion
    resp = app_user.post_resource(path, IDocumentVersion, {})
    return resp


def _batch_post_full_sample_proposal(app_user) -> TestResponse:
    subrequests = _create_proposal()
    resp = app_user.batch(subrequests)
    return resp


@mark.functional
@mark.usefixtures('log')
class TestMercatorWorkflow:

    def test_draft_participant_cannot_create_proposal(self, app_participant):
        from adhocracy_mercator.resources.mercator import IMercatorProposal
        assert IMercatorProposal not in app_participant.get_postable_types('/')

    def test_draft_participant_cannot_create_proposal_per_batch(self, app_anonymous):
        resp = _batch_post_full_sample_proposal(app_anonymous)
        assert resp.status_code == 403

    def test_change_state_to_announce(self, app_initiator):
        resp = do_transition_to(app_initiator, '/', 'announce')
        assert resp.status_code == 200

    def test_announce_participant_cannot_create_proposal(self, app_participant):
        from adhocracy_mercator.resources.mercator import IMercatorProposal
        assert IMercatorProposal not in app_participant.get_postable_types('/')

    def test_change_state_to_participate(self, app_initiator):
        resp = do_transition_to(app_initiator, '/', 'participate')
        assert resp.status_code == 200

    def test_participate_participant_can_create_proposal(self, app_participant):
        resp = _post_proposal_item(app_participant, path='/')
        resp = _post_proposal_version(app_participant, path='/proposal_0000000')
        assert resp.status_code == 200

    def test_participate_can_edit_proposal(self, app_participant):
        from adhocracy_mercator.resources import mercator
        possible_types = mercator.mercator_proposal_meta.element_types
        postable_types = app_participant.get_postable_types('/proposal_0000000')
        assert set(postable_types) == set(possible_types)

    def test_participate_can_create_and_update_proposal_per_batch(self, app_participant):
        """Create full proposal then do batch request that first
         creates a new subresource Version (IOrganisationInfo) and then
         creates a new proposal Version manually (IUserInfo).

        Fix regression issue #697
        """
        resp = app_participant.batch(create_proposal_batch)
        resp = app_participant.batch(update_proposal_batch)
        assert app_participant.get('/proposal_0000001/VERSION_0000001').json_body['data']['adhocracy_mercator.sheets.mercator.IUserInfo']['personal_name'] == 'pita Updated'
        assert "VERSION_0000001" in app_participant.get('/proposal_0000001/VERSION_0000001').json_body['data']['adhocracy_mercator.sheets.mercator.IMercatorSubResources']['organization_info']

    def test_participate_cannot_edit_other_users_proposal(self, app_participant, app_god):
        resp = _post_proposal_item(app_god, path='/')
        proposal = resp.json['path']
        _post_proposal_version(app_god, path=proposal)
        postable_types = app_participant.get_postable_types(proposal)
        assert postable_types == []

    def test_change_state_to_frozen(self, app_initiator):
        resp = do_transition_to(app_initiator, '/', 'evaluate')
        assert resp.status_code == 200

    def test_frozen_participant_cannot_create_proposal_item(self, app_participant):
        from adhocracy_mercator.resources.mercator import IMercatorProposal
        assert IMercatorProposal not in app_participant.get_postable_types('/')

    def test_frozen_participant_cannot_edit_proposal(self, app_participant):
        postable_types =  app_participant.get_postable_types('/proposal_0000000')
        assert postable_types == []

    def test_change_state_to_result(self, app_initiator):
        resp = do_transition_to(app_initiator, '/', 'result')
        assert resp.status_code == 200

    def test_result_participant_cannot_create_proposal_item(self, app_participant):
        from adhocracy_mercator.resources.mercator import IMercatorProposal
        assert IMercatorProposal not in app_participant.get_postable_types('/')

    def test_result_participant_can_edit_proposal(self, app_participant):
        from adhocracy_mercator.resources import mercator
        possible_types = mercator.mercator_proposal_meta.element_types
        postable_types = app_participant.get_postable_types('/proposal_0000000')
        assert set(postable_types) == set(possible_types)

    def test_result_participant_can_create_logbook_documents(self,
                                                             app_participant):
        resp = _post_document_item(app_participant, path='/proposal_0000000/logbook')
        resp = _post_document_version(app_participant, path='/proposal_0000000/logbook/document_0000000')
        assert resp.status_code == 200

    def test_result_participate_cannot_edit_other_users_logbook(self,
                                                                app_god,
                                                                app_participant):
        resp = _post_proposal_item(app_god, path='/')
        proposal = resp.json['path']
        resp = _post_proposal_version(app_god, path=proposal)
        postable_types = app_participant.get_postable_types( proposal + 'logbook')
        assert postable_types == []

    def test_result_participant_can_search_proposals(self, app_participant, rest_url):
        from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
        from adhocracy_core.sheets.pool import IPool
        params = dict(content_type=IMercatorProposalVersion.__identifier__,
                      count=True,
                      limit=50,
                      mercator_requested_funding=5000,
                      reverse=True,
                      sort='item_creation_date',
                      depth='all',
                      tag='LAST',
                      )
        resp = app_participant.get('/', params=params).json
        assert resp['data'][IPool.__identifier__]['elements'] == \
            [rest_url + '/mercator/proposal_0000001/VERSION_0000001/']



