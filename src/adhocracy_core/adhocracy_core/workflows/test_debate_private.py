from pytest import fixture
from pytest import mark

from adhocracy_core.testing import add_resources
from adhocracy_core.testing import do_transition_to


@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration


@mark.usefixtures('integration')
def test_includeme(registry):
    from adhocracy_core.workflows import ACLLocalRolesWorkflow
    workflow = registry.content.workflows['debate_private']
    assert isinstance(workflow, ACLLocalRolesWorkflow)


@mark.functional
class TestDebatePrivateProcess:

    @fixture
    def process_url(self):
        return '/opin/collaborative_text'

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
        debate_process_meta = process_meta._replace(workflow_name='debate_private')
        add_resource_type_to_registry(debate_process_meta, configurator)
        app_router = configurator.make_wsgi_app()
        return app_router

    def test_create_resources(self, process_url, datadir, app_admin):
        json_file_private = str(datadir.join('private.json'))
        add_resources(app_admin.app_router, json_file_private)
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

    def test_set_process_state_announce(self, process_url, app_admin):
        resp = do_transition_to(app_admin, process_url, 'announce')
        assert resp.status_code == 200

    def test_announce_anonymous_cannot_read_private_process(
            self, process_url, app_anonymous):
        resp = app_anonymous.get(process_url)
        assert resp.status_code == 403

    def test_announce_authenticated_cannot_read_private_process(
            self, process_url, app_authenticated):
        resp = app_authenticated.get(process_url)
        assert resp.status_code == 403

    def test_set_process_participate_state(self, process_url, app_admin):
        resp = do_transition_to(app_admin, process_url, 'participate')
        assert resp.status_code == 200

    def test_participate_anonymous_cannot_read_private_process(
            self, process_url, app_anonymous):
        resp = app_anonymous.get(process_url)
        assert resp.status_code == 403

    def test_participate_authenticated_cannot_read_private_process(
            self, process_url, app_authenticated):
        resp = app_authenticated.get(process_url)
        assert resp.status_code == 403

    def test_set_process_evaluate_state(self, process_url, app_admin):
        resp = do_transition_to(app_admin, process_url, 'evaluate')
        assert resp.status_code == 200

    def test_evaluate_anonymous_cannot_read_private_process(
            self, process_url, app_anonymous):
        resp = app_anonymous.get(process_url)
        assert resp.status_code == 403

    def test_evaluate_authenticated_cannot_read_private_process(
            self, process_url, app_authenticated):
        resp = app_authenticated.get(process_url)
        assert resp.status_code == 403

    def test_set_process_state_result(self, process_url, app_admin):
        resp = do_transition_to(app_admin, process_url, 'result')
        assert resp.status_code == 200

    def test_result_anonymous_cannot_read_private_process(
            self, process_url, app_anonymous):
        resp = app_anonymous.get(process_url)
        assert resp.status_code == 403

    def test_result_authenticated_cannot_read_private_process(
            self, process_url, app_authenticated):
        resp = app_authenticated.get(process_url)
        assert resp.status_code == 403

    def test_set_process_evaluate_closed(self, process_url, app_admin):
        resp = do_transition_to(app_admin, process_url, 'closed')
        assert resp.status_code == 200

    def test_closed_anonymous_cannot_read_private_process(
            self, process_url, app_anonymous):
        resp = app_anonymous.get(process_url)
        assert resp.status_code == 403

    def test_closed_authenticated_cannot_read_private_process(
            self, process_url, app_authenticated):
        resp = app_authenticated.get(process_url)
        assert resp.status_code == 403
