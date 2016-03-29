from pyramid.traversal import find_resource
from pyramid import testing
from pytest import fixture
from pytest import mark
from adhocracy_core.testing import add_resources
from adhocracy_core.testing import do_transition_to


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
    assert workflow.state_of(context) == 'draft'
    workflow.transition_to_state(context, request, 'announce')
    assert workflow.state_of(context) == 'announce'
    workflow.transition_to_state(context, request, 'participate')
    assert workflow.state_of(context) == 'participate'
    workflow.transition_to_state(context, request, 'evaluate')
    assert workflow.state_of(context) == 'evaluate'
    workflow.transition_to_state(context, request, 'result')
    assert workflow.state_of(context) == 'result'
    workflow.transition_to_state(context, request, 'closed')
    assert workflow.state_of(context) == 'closed'


@mark.functional
class TestStandardPublicWithPrivateProcessesConfig:

    @fixture
    def process_url_public(self):
        return '/opin/idea_collection'

    @fixture(scope='class')
    def app_settings(self, app_settings) -> dict:
        """Return settings to start the test wsgi app."""
        app_settings['adhocracy.skip_registration_mail'] = True
        return app_settings

    @fixture(scope='class')
    def app_router(self, app_settings):
        """Add a `debate_private` workflow to IProcess resources."""
        from adhocracy_core.testing import make_configurator
        from adhocracy_core.resources import add_resource_type_to_registry
        from adhocracy_core.resources.process import process_meta
        import adhocracy_core
        configurator = make_configurator(app_settings, adhocracy_core)
        standard_process_meta = process_meta._replace(workflow_name='standard')
        add_resource_type_to_registry(standard_process_meta, configurator)
        app_router = configurator.make_wsgi_app()
        return app_router

    def test_create_resources(self,
                              datadir,
                              process_url_public,
                              app_admin):
        json_file_public = str(datadir.join('public.json'))
        add_resources(app_admin.app_router, json_file_public)
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200

    def set_process_state(self, process_url, app_admin, state):
        resp = do_transition_to(app_admin,
                                process_url,
                                state)
        assert resp.status_code == 200

    def test_announce_authenticated_can_read_public_process(
            self, process_url_public, app_authenticated, app_admin):
        self.set_process_state(process_url_public,
                               app_admin,
                               'announce')
        resp = app_authenticated.get(process_url_public)
        assert resp.status_code == 200

    def test_announce_anonymous_can_read_public_process(
            self, process_url_public, app_anonymous):
        resp = app_anonymous.get(process_url_public)
        assert resp.status_code == 200

    def test_announce_initiator_can_read_public_process(
            self, process_url_public, app_initiator):
        resp = app_initiator.get(process_url_public)
        assert resp.status_code == 200

    def test_announce_moderator_can_read_public_process(
            self, process_url_public, app_moderator):
        resp = app_moderator.get(process_url_public)
        assert resp.status_code == 200

    def test_announce_admin_can_read_public_process(
            self, process_url_public, app_admin):
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200

    def test_participate_authenticated_can_read_public_process(
            self, process_url_public, app_authenticated, app_admin):
        self.set_process_state(process_url_public, app_admin, 'participate')
        resp = app_authenticated.get(process_url_public)
        assert resp.status_code == 200

    def test_participate_anonymous_can_read_public_process(
            self, process_url_public, app_anonymous):
        resp = app_anonymous.get(process_url_public)
        assert resp.status_code == 200

    def test_participate_initiator_can_read_public_process(
            self, process_url_public, app_initiator):
        resp = app_initiator.get(process_url_public)
        assert resp.status_code == 200

    def test_participate_moderator_can_read_public_process(
            self, process_url_public, app_moderator):
        resp = app_moderator.get(process_url_public)
        assert resp.status_code == 200

    def test_participate_admin_can_read_public_process(
            self, process_url_public, app_admin):
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200

    def test_evaluate_authenticated_can_read_public_process(
            self, process_url_public, app_authenticated, app_admin):
        self.set_process_state(process_url_public, app_admin, 'evaluate')
        resp = app_authenticated.get(process_url_public)
        assert resp.status_code == 200

    def test_evaluate_anonymous_can_read_public_process(
            self, process_url_public, app_anonymous):
        resp = app_anonymous.get(process_url_public)
        assert resp.status_code == 200

    def test_evaluate_initiator_can_read_public_process(
            self, process_url_public, app_initiator):
        resp = app_initiator.get(process_url_public)
        assert resp.status_code == 200

    def test_evaluate_moderator_can_read_public_process(
            self, process_url_public, app_moderator):
        resp = app_moderator.get(process_url_public)
        assert resp.status_code == 200

    def test_evaluate_admin_can_read_public_process(
            self, process_url_public, app_admin):
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200

    def test_result_authenticated_can_read_public_process(
            self, process_url_public, app_authenticated, app_admin):
        self.set_process_state(process_url_public, app_admin, 'result')
        resp = app_authenticated.get(process_url_public)
        assert resp.status_code == 200

    def test_result_anonymous_can_read_public_process(
            self, process_url_public, app_anonymous):
        resp = app_anonymous.get(process_url_public)
        assert resp.status_code == 200

    def test_result_initiator_can_read_public_process(
            self, process_url_public, app_initiator):
        resp = app_initiator.get(process_url_public)
        assert resp.status_code == 200

    def test_result_moderator_can_read_public_process(
            self, process_url_public, app_moderator):
        resp = app_moderator.get(process_url_public)
        assert resp.status_code == 200

    def test_result_admin_can_read_public_process(
            self, process_url_public, app_admin):
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200

    def test_closed_authenticated_can_read_public_process(
            self, process_url_public, app_authenticated, app_admin):
        self.set_process_state(process_url_public, app_admin, 'closed')
        resp = app_authenticated.get(process_url_public)
        assert resp.status_code == 200

    def test_closed_anonymous_can_read_public_process(
            self, process_url_public, app_anonymous):
        resp = app_anonymous.get(process_url_public)
        assert resp.status_code == 200

    def test_closed_initiator_can_read_public_process(
            self, process_url_public, app_initiator):
        resp = app_initiator.get(process_url_public)
        assert resp.status_code == 200

    def test_closed_moderator_can_read_public_process(
            self, process_url_public, app_moderator):
        resp = app_moderator.get(process_url_public)
        assert resp.status_code == 200

    def test_closed_admin_can_read_public_process(
            self, process_url_public, app_admin):
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200
