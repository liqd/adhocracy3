from pytest import fixture
from pytest import mark
from webtest import TestResponse

from adhocracy_core.testing import add_resources
from adhocracy_core.testing import do_transition_to


def _post_document_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.proposal import IGeoProposal
    resp = app_user.post_resource(path, IGeoProposal, {})
    return resp


@mark.functional
class TestIdeaCollection:

    @fixture
    def process_url(self):
        return '/organisation/idea_collection'

    def test_create_resources(self,
                              datadir,
                              process_url,
                              app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app_admin.app_router, json_file)
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

    def test_set_participate_state(self, process_url, app_admin):
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url,
                                'announce')
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url,
                                'participate')
        assert resp.status_code == 200

    def test_participate_initiator_creates_document(self,
                                                    process_url,
                                                    app_initiator):
        resp = _post_document_item(app_initiator, path=process_url)
        assert resp.status_code == 200
