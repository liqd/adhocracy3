from pyramid.traversal import find_resource
from pytest import fixture
from pytest import mark
from webtest import TestResponse

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
        json_file_private = str(datadir.join('private.json'))
        add_resources(app_admin.app_router, json_file_private)
        json_file_public = str(datadir.join('public.json'))
        add_resources(app_admin.app_router, json_file_public)
        root = get_root(app_admin.app_router)
        process_private = find_resource(root, process_url_private)
        set_local_roles(process_private,
                        {"opin-idea-collection-participants":
                         {"role:participant"}})
        process_public = find_resource(root, process_url_public)
        set_local_roles(process_public,
                        {"group:authenticated":
                         {"role:participant"}})
        resp = app_admin.get(process_url_private)
        assert resp.status_code == 200
        resp = app_admin.get(process_url_public)
        assert resp.status_code == 200

    def test_set_private_process_participate_state(self,
                                                   registry,
                                                   process_url_private,
                                                   app_admin):
        process_public = find_resource(get_root(app_admin.app_router), process_url_private)
        # TODO, FIXME here the __local_roles__ attribute is not there anymore
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
                                                  registry,
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

    def test_participate_participant_cannot_read_private_process(
            self, registry, process_url_private, app_participant):
        import pudb; pudb.set_trace() #  noqa
        resp = app_participant.get(process_url_private)
        assert resp.status_code == 403
