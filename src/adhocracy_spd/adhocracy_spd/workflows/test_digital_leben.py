"""
Test the digital leben workflow, which is now in core named
'debate'. Acts as a regression test.

"""
from pyramid import testing
from pytest import fixture
from pytest import mark
from webtest import TestResponse

from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to


def _post_document_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.document import IDocument
    resp = app_user.post_resource(path, IDocument, {})
    return resp


@mark.functional
class TestDigitalLebenWorkflow:

    @fixture
    def process_url(self):
        return '/digital_leben'

    def test_create_resources(self,
                              registry,
                              datadir,
                              process_url,
                              app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app_admin.app_router, json_file)
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

    def test_draft_admin_can_view_process(self, app_admin, registry):
        resp = app_admin.get('/digital_leben')
        assert resp.status_code == 200

    def test_draft_participant_cannot_view_process(self, app_participant):
        resp = app_participant.get('/digital_leben')
        assert resp.status_code == 403

    def test_draft_participant_cannot_create_document(self, app_participant, registry):
        from adhocracy_core.resources.document import IDocument
        assert IDocument not in app_participant.get_postable_types('/digital_leben')

    def test_change_state_to_announce(self, app_initiator, registry):
        resp = do_transition_to(app_initiator, '/digital_leben', 'announce')
        assert resp.status_code == 200

    def test_change_state_to_participate(self, app_initiator, registry):
        resp = do_transition_to(app_initiator, '/digital_leben', 'participate')
        assert resp.status_code == 200

    def test_participate_initiator_creates_document(self, app_initiator, registry):
        resp = _post_document_item(app_initiator, path='/digital_leben')
        assert resp.status_code == 200

    def test_participate_participant_cannot_create_document(self,
                                                            app_participant,
                                                            registry):
        from adhocracy_core.resources.document import IDocument
        assert IDocument not in app_participant.get_postable_types('/digital_leben')

    def test_participate_participant_can_comment_document(self,
                                                          app_participant,
                                                          registry):
        from adhocracy_core.resources.comment import IComment
        assert IComment in app_participant.get_postable_types(
            '/digital_leben/document_0000000/comments')

    def test_participate_participant_can_rate_document(self,
                                                       app_participant,
                                                       registry):
        from adhocracy_core.resources.rate import IRate
        assert IRate in app_participant.get_postable_types(
            '/digital_leben/document_0000000/rates')

    def test_change_state_to_evaluate(self,
                                      app_initiator,
                                      registry):
        resp = do_transition_to(app_initiator, '/digital_leben', 'evaluate')
        assert resp.status_code == 200

    def test_change_state_to_result(self, app_initiator, registry):
        resp = do_transition_to(app_initiator, '/digital_leben', 'result')
        assert resp.status_code == 200

    def test_result_participant_can_view_process(self,
                                                 app_participant,
                                                 registry):
        resp = app_participant.get('/digital_leben')
        assert resp.status_code == 200

    def test_result_participant_cannot_comment_document(self,
                                                        app_participant,
                                                        registry):
        from adhocracy_core.resources.comment import IComment
        assert IComment not in app_participant.get_postable_types(
            '/digital_leben/document_0000000/comments')

    def test_result_participant_cannot_rate_document(self,
                                                     app_participant,
                                                     registry):
        from adhocracy_core.resources.rate import IRate
        assert IRate not in app_participant.get_postable_types(
            '/digital_leben/document_0000000/rates')

    def test_change_state_to_closed(self, app_initiator, registry):
        resp = do_transition_to(app_initiator, '/digital_leben', 'closed')
        assert resp.status_code == 200
