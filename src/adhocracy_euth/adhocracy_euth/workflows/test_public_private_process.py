from pytest import fixture
from pytest import mark

from adhocracy_core.testing import add_resources
from adhocracy_core.testing import add_local_roles
from adhocracy_core.testing import do_transition_to


@mark.functional
class TestPrivatePublicProcess:

    @fixture
    def process_url_private(self):
        return '/opin/collaborative_text'

    @fixture
    def process_url_public(self):
        return '/opin/idea_collection'

    def test_create_resources(self,
                              datadir,
                              process_url_private,
                              process_url_public,
                              app_admin):
        private = str(datadir.join('private.json'))
        add_resources(app_admin.app_router, private)
        public = str(datadir.join('public.json'))
        add_resources(app_admin.app_router, public)

        resp = app_admin.get(process_url_private)
        assert resp.status_code == 200
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200

    def test_set_private_process_participate_state(self,
                                                   process_url_private,
                                                   app_admin):
        resp = app_admin.get(process_url_private)
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url_private,
                                'announce')
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url_private,
                                'participate')
        assert resp.status_code == 200

    def test_set_public_process_participate_state(self,
                                                  process_url_public,
                                                  app_admin):
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url_public,
                                'announce')
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url_public,
                                'participate')
        assert resp.status_code == 200

    def test_participate_authenticated_cannot_read_private_process(
            self, process_url_private, app_authenticated):
        """The authenticated test user has no gobal role but is member ob the
        default user group.
        """
        resp = app_authenticated.get(process_url_private)
        assert resp.status_code == 403

    def test_participate_authenticated_can_read_prublic_process(
            self, process_url_public, app_authenticated):
        resp = app_authenticated.get(process_url_public)
        assert resp.status_code == 200
