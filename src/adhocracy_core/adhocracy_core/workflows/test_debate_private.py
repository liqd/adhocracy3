from pyramid.traversal import find_resource
from pytest import fixture
from pytest import mark
import transaction

from adhocracy_core.authorization import acm_to_acl
from adhocracy_core.authorization import get_acl
from adhocracy_core.authorization import set_acl
from adhocracy_core.authorization import set_local_roles
from adhocracy_core.schema import ACM
from adhocracy_core.utils import get_root
from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to


@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration


@mark.usefixtures('integration')
def test_includeme(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['debate_private']
    assert isinstance(workflow, AdhocracyACLWorkflow)


@mark.functional
@mark.xfail(True, reason='Fix change database while running functional tests.')
class TestDebatePrivateProcess:

    @fixture
    def process_url_private(self):
        return '/opin/collaborative_text'

    @fixture(scope='session')
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

    def test_create_resources(self,
                              datadir,
                              process_url_private,
                              app_admin):
        registry = app_admin.app_router.registry
        root = get_root(app_admin.app_router)
        json_file_private = str(datadir.join('private.json'))
        add_resources(app_admin.app_router, json_file_private)
        process_private = find_resource(root, process_url_private)
        set_local_roles(process_private,
                        {"opin-idea-collection-participants":
                         {"role:participant"}})
        old_acl = get_acl(root)
        acm = ACM().deserialize(
            {'principals':            ['anonymous', 'authenticated', 'participant', 'moderator',  'creator', 'initiator', 'admin'],
             'permissions': [['view',  'Allow',      'Deny',          'Allow',       'Allow',      'Allow',   'Allow',     'Allow'],
             ]})
        new_acl = acm_to_acl(acm, registry) + old_acl
        set_acl(root, new_acl)
        transaction.commit()
        resp = app_admin.get(process_url_private)
        assert resp.status_code == 200

    def set_process_state(self,
                          process_url,
                          app_admin,
                          state):
        resp = do_transition_to(app_admin,
                                process_url,
                                state)
        assert resp.status_code == 200

    def test_announce_anonymous_cannot_read_private_process(
            self, process_url_private, app_anonymous, app_admin):
        self.set_process_state(process_url_private, app_admin, 'announce')
        resp = app_anonymous.get(process_url_private)
        assert resp.status_code == 403

    def test_announce_authenticated_cannot_read_private_process(
            self, process_url_private, app_authenticated):
        resp = app_authenticated.get(process_url_private)
        assert resp.status_code == 403


    def set_process_participate_state(self,
                                      process_url,
                                      app_admin):
        resp = do_transition_to(app_admin,
                                process_url,
                                'participate')
        assert resp.status_code == 200

    def test_participate_anonymous_cannot_read_private_process(
            self, process_url_private, app_anonymous, app_admin):
        self.set_process_state(process_url_private, app_admin, 'participate')
        resp = app_anonymous.get(process_url_private)
        assert resp.status_code == 403

    def test_participate_authenticated_cannot_read_private_process(
            self, process_url_private, app_authenticated, app_admin):
        resp = app_authenticated.get(process_url_private)
        assert resp.status_code == 403

    def test_evaluate_anonymous_cannot_read_private_process(
            self, process_url_private, app_anonymous, app_admin):
#        import pudb; pudb.set_trace() #  noqa
        self.set_process_state(process_url_private, app_admin, 'evaluate')
        resp = app_anonymous.get(process_url_private)
        assert resp.status_code == 403

    def test_evaluate_authenticated_cannot_read_private_process(
            self, process_url_private, app_authenticated, app_admin):
        resp = app_authenticated.get(process_url_private)
        assert resp.status_code == 403

    def set_process_state(self,
                          process_url,
                          app_admin,
                          state):
        resp = do_transition_to(app_admin,
                                process_url,
                                state)
        assert resp.status_code == 200

    def test_result_anonymous_cannot_read_private_process(
            self, process_url_private, app_anonymous, app_admin):
        self.set_process_state(process_url_private, app_admin, 'result')
        resp = app_anonymous.get(process_url_private)
        assert resp.status_code == 403

    def test_result_authenticated_cannot_read_private_process(
            self, process_url_private, app_authenticated, app_admin):
        resp = app_authenticated.get(process_url_private)
        assert resp.status_code == 403

    def test_closed_anonymous_cannot_read_private_process(
            self, process_url_private, app_anonymous, app_admin):
        self.set_process_state(process_url_private,
                               app_admin,
                               'closed')
        resp = app_anonymous.get(process_url_private)
        assert resp.status_code == 403

    def test_closed_authenticated_cannot_read_private_process(
            self, process_url_private, app_authenticated, app_admin):
        resp = app_authenticated.get(process_url_private)
        assert resp.status_code == 403
