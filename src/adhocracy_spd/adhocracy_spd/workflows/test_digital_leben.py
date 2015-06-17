from pyramid import testing
from pytest import fixture
from pytest import mark
from webtest import TestResponse


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_spd.workflows')


@mark.usefixtures('integration')
def test_includeme_add_sample_workflow(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['digital_leben']
    assert isinstance(workflow, AdhocracyACLWorkflow)


@mark.usefixtures('integration')
def test_initiate_and_transition_to_announce(registry, context):
    workflow = registry.content.workflows['digital_leben']
    request = testing.DummyRequest()
    assert workflow.state_of(context) is None
    workflow.initialize(context)
    assert workflow.state_of(context) is 'draft'
    workflow.transition_to_state(context, request, 'participate')
    assert workflow.state_of(context) is 'participate'
    workflow.transition_to_state(context, request, 'frozen')
    assert workflow.state_of(context) is 'frozen'
    workflow.transition_to_state(context, request, 'result')
    assert workflow.state_of(context) is 'result'


def _post_document_item(app_user, name='', path='') -> TestResponse:
    from adhocracy_core.resources.document import IDocument
    from adhocracy_core.sheets.name import IName
    sheets_cstruct = {IName.__identifier__: {'name': name}}
    resp = app_user.post_resource(path, IDocument, sheets_cstruct)
    return resp


def _do_transition_to(app_user, path, state) -> TestResponse:
    from adhocracy_spd.sheets.digital_leben import IWorkflowAssignment
    data = {'data': {IWorkflowAssignment.__identifier__:\
                         {'workflow_state': state}}}
    resp = app_user.put(path, data)
    return resp


@mark.functional
class TestDigitalLebenWorkflow:

    def test_draft_admin_can_view_process(self, app_admin):
        resp = app_admin.get('/digital_leben')
        assert resp.status_code == 200

    def test_draft_participant_cannot_view_process(self, app_participant):
        resp = app_participant.get('/digital_leben')
        assert resp.status_code == 403

    def test_draft_participant_cannot_create_document(self, app_participant):
        from adhocracy_core.resources.document import IDocument
        assert IDocument not in app_participant.get_postable_types('/digital_leben')

    def test_change_state_to_participate(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/digital_leben', 'participate')
        assert resp.status_code == 200

    def test_participate_initiator_creates_document(self, app_initiator):
        resp = _post_document_item(app_initiator, path='/digital_leben',
                                   name='document')
        assert resp.status_code == 200

    def test_participate_participant_cannot_create_document(self,
                                                            app_participant):
        from adhocracy_core.resources.document import IDocument
        assert IDocument not in app_participant.get_postable_types('/digital_leben')

    def test_participate_participant_can_comment_document(self,
                                                          app_participant):
        from adhocracy_core.resources.comment import IComment
        assert IComment in app_participant.get_postable_types(
            '/digital_leben/document/comments')

    def test_participate_participant_can_rate_document(self, app_participant):
        from adhocracy_core.resources.rate import IRate
        assert IRate in app_participant.get_postable_types(
            '/digital_leben/document/rates')

    def test_change_state_to_frozen(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/digital_leben', 'frozen')
        assert resp.status_code == 200

    def test_frozen_participant_can_view_process(self, app_participant):
        resp = app_participant.get('/digital_leben')
        assert resp.status_code == 200

    def test_frozen_participant_cannot_comment_document(self, app_participant):
        from adhocracy_core.resources.comment import IComment
        assert IComment not in app_participant.get_postable_types(
            '/digital_leben/document/comments')

    def test_frozen_participant_cannot_rate_document(self, app_participant):
        from adhocracy_core.resources.rate import IRate
        assert IRate not in app_participant.get_postable_types(
            '/digital_leben/document/rates')

    def test_change_state_to_result(self, app_initiator):
        resp = _do_transition_to(app_initiator, '/digital_leben', 'result')
        assert resp.status_code == 200
