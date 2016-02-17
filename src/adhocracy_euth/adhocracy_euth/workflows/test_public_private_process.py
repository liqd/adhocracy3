from pyramid.traversal import find_resource
from pytest import fixture
from pytest import mark
from webtest import TestResponse
import transaction

from adhocracy_core.authorization import set_local_roles
from adhocracy_core.utils import get_root
from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to


@mark.functional
class TestPrivatePublicProcess:

    @fixture
    def process_url_private(self):
        return '/opin/collaborative_text'

    @fixture
    def process_url_public(self):
        return '/opin/idea_collection'

    def test_create_resources(self,
                              registry,
                              datadir,
                              process_url_private,
                              process_url_public,
                              app_admin):
        root = get_root(app_admin.app_router)
        json_file_private = str(datadir.join('private.json'))
        add_resources(app_admin.app_router, json_file_private)
        json_file_public = str(datadir.join('public.json'))
        add_resources(app_admin.app_router, json_file_public)
        process_private = find_resource(root, process_url_private)
        set_local_roles(process_private,
                        {"opin-idea-collection-participants":
                         {"role:participant"}})
        transaction.commit()
        process_public = find_resource(root, process_url_public)
        set_local_roles(process_public,
                        {"group:authenticated":
                         {"role:participant"},})
        transaction.commit()
        resp = app_admin.get(process_url_private)
        assert resp.status_code == 200
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200

    def test_set_private_process_participate_state(self,
                                                   registry,
                                                   process_url_private,
                                                   app_god):
        resp = app_god.get(process_url_private)
        assert resp.status_code == 200

        resp = do_transition_to(app_god,
                                process_url_private,
                                'announce')
        assert resp.status_code == 200

        resp = do_transition_to(app_god,
                                process_url_private,
                                'participate')
        assert resp.status_code == 200


    def test_set_public_process_participate_state(self,
                                                  registry,
                                                  process_url_public,
                                                  app_god):
        resp = app_god.get(process_url_public)
        assert resp.status_code == 200

        resp = do_transition_to(app_god,
                                process_url_public,
                                'announce')
        assert resp.status_code == 200

        resp = do_transition_to(app_god,
                                process_url_public,
                                'participate')
        assert resp.status_code == 200

    def test_participate_anonymous_cannot_read_private_process(
            self, registry, process_url_private, app_anonymous):
        resp = app_anonymous.get(process_url_private)
        assert resp.status_code == 403

    def test_participate_authenticated_cannot_read_private_process(
            self, registry, process_url_private, app_authenticated):
        resp = app_authenticated.get(process_url_private)
        assert resp.status_code == 403

    def test_participate_authenticated_can_read_public_process(
            self, registry, process_url_public, app_authenticated, app_god):
        resp = app_authenticated.get(process_url_public)
        assert resp.status_code == 200

    def test_participate_anonymous_can_read_public_process(
            self, registry, process_url_public, app_anonymous):
        root = get_root(app_anonymous.app_router)
        resp = app_anonymous.get(process_url_public)
        assert resp.status_code == 200

    def test_participate_initiator_can_read_public_process(
            self, registry, process_url_public, app_initiator):
        root = get_root(app_initiator.app_router)
        resp = app_initiator.get(process_url_public)
        assert resp.status_code == 200

    def test_participate_moderator_can_read_public_process(
            self, registry, process_url_public, app_moderator):
        root = get_root(app_moderator.app_router)
        resp = app_moderator.get(process_url_public)
        assert resp.status_code == 200

    def test_participate_admin_can_read_public_process(
            self, registry, process_url_public, app_admin):
        root = get_root(app_admin.app_router)
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200
