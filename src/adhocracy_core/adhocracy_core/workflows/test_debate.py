from pyramid import testing
from pyramid.threadlocal import manager
from pyramid.traversal import find_resource
from pytest import fixture
from pytest import mark
from webtest import TestResponse
import transaction

from adhocracy_core.utils.testing import add_resources
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


def _post_document_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.document import IDocument
    resp = app_user.post_resource(path, IDocument, {})
    return resp


@mark.functional
class TestDebateWorkflow:

    @fixture(scope='class')
    def app_router(self, app_settings):
        """Add `debate` workflow to IProcess resources and return wsgi app."""
        from adhocracy_core.testing import make_configurator
        from adhocracy_core.resources import add_resource_type_to_registry
        from adhocracy_core.resources.process import process_meta
        import adhocracy_core
        configurator = make_configurator(app_settings, adhocracy_core)
        debate_process_meta = process_meta._replace(workflow_name='debate')
        add_resource_type_to_registry(debate_process_meta, configurator)
        app_router = configurator.make_wsgi_app()
        return app_router

    def test_create_debate_process(self,
                                   datadir,
                                   app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app_admin.app_router, json_file)
        resp = app_admin.get('/debate')
        assert resp.status_code == 200

    def test_draft_admin_can_view_process(self, app_admin):
        resp = app_admin.get('/debate')
        assert resp.status_code == 200

    def test_draft_participant_cannot_view_process(self, app_participant):
        resp = app_participant.get('/debate')
        assert resp.status_code == 403

    def test_draft_participant_cannot_create_document(self,
                                                      app_participant):
        from adhocracy_core.resources.document import IDocument
        assert IDocument not in app_participant.get_postable_types('/debate')

    def test_change_state_to_announce(self, app_initiator):
        resp = do_transition_to(app_initiator, '/debate', 'announce')
        assert resp.status_code == 200

    def test_change_state_to_participate(self, app_initiator):
        resp = do_transition_to(app_initiator, '/debate', 'participate')
        assert resp.status_code == 200

    def test_participate_initiator_creates_document(self,
                                                    app_initiator):
        resp = _post_document_item(app_initiator, path='/debate')
        assert resp.status_code == 200

    def test_participate_participant_cannot_create_document(self,
                                                            app_participant):
        from adhocracy_core.resources.document import IDocument
        assert IDocument not in app_participant.get_postable_types('/debate')

    def test_participate_participant_can_comment_document(self,
                                                          app_participant):
        from adhocracy_core.resources.comment import IComment
        assert IComment in app_participant.get_postable_types(
            '/debate/document_0000000/comments')

    def test_participate_participant_can_rate_document(self,
                                                       app_participant):
        from adhocracy_core.resources.rate import IRate
        assert IRate in app_participant.get_postable_types(
            '/debate/document_0000000/rates')

    def test_change_state_to_evaluate(self,
                                      app_initiator):
        resp = do_transition_to(app_initiator, '/debate', 'evaluate')
        assert resp.status_code == 200

    def test_change_state_to_result(self, app_initiator):
        resp = do_transition_to(app_initiator, '/debate', 'result')
        assert resp.status_code == 200

    def test_result_participant_can_view_process(self,
                                                 app_participant):
        resp = app_participant.get('/debate')
        assert resp.status_code == 200

    def test_result_participant_cannot_comment_document(self,
                                                        app_participant):
        from adhocracy_core.resources.comment import IComment
        assert IComment not in app_participant.get_postable_types(
            '/debate/document_0000000/comments')

    def test_result_participant_cannot_rate_document(self,
                                                     app_participant):
        from adhocracy_core.resources.rate import IRate
        assert IRate not in app_participant.get_postable_types(
            '/debate/document_0000000/rates')

    def test_change_state_to_closed(self, app_initiator):
        resp = do_transition_to(app_initiator, '/debate', 'closed')
        assert resp.status_code == 200
