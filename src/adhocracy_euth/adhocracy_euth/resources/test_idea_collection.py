from pytest import mark
from pytest import fixture
from webtest import TestResponse

from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to


class TestProcess:

    @fixture
    def meta(self):
        from .idea_collection import process_meta
        return process_meta

    def test_meta(self, meta):
        from adhocracy_core.resources.proposal import IProposal
        assert meta.element_types == (IProposal,)
        assert meta.workflow_name == 'standard'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


def _post_proposal_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.proposal import IProposal
    resp = app_user.post_resource(path, IProposal, {})
    return resp


@mark.functional
class TestIdeaCollection:

    @fixture
    def process_url(self):
        return '/opin/idea_collection'

    def test_create_resources(self,
                              registry,
                              datadir,
                              process_url,
                              app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app_admin.app_router, json_file)
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

    def test_set_participate_state(self, registry, process_url, app_admin):
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

    def test_participate_participant_creates_proposal(self,
                                                      registry,
                                                      process_url,
                                                      app_participant):
        resp = _post_proposal_item(app_participant, path=process_url)
        assert resp.status_code == 200
