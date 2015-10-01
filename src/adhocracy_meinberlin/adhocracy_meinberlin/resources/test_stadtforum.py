from distutils import dir_util
import os
import transaction

from pytest import fixture
from pytest import mark
from webtest import TestResponse

from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to

class TestProcess:

    @fixture
    def meta(self):
        from .stadtforum import process_meta
        return process_meta

    def test_meta(self, meta):
        from .stadtforum import IProcess
        assert meta.iresource is IProcess
        assert meta.workflow_name == 'standard'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


def _post_proposal_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.proposal import IProposal
    resp = app_user.post_resource(path, IProposal, {})
    return resp

def _post_comment_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.comment import IComment
    resp = app_user.post_resource(path, IComment, {})
    return resp

def _post_polarization_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.relation import IPolarization
    resp = app_user.post_resource(path, IPolarization, {})
    return resp


@mark.functional
class TestStadtForum:

    @fixture
    def process_url(self):
        return '/organisation/stadtforum'

    def test_create_resources(self,
                              registry,
                              datadir,
                              process_url,
                              app,
                              app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app, json_file)
        resp = app_admin.get(process_url)
        assert resp.status_code == 200


    def test_set_participate_state(self, registry, app, process_url, app_admin):
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
                                                      app,
                                                      process_url,
                                                      app_participant):
        resp = _post_proposal_item(app_participant, path=process_url)
        assert resp.status_code == 200


    def test_participate_participant_creates_comment(self,
                                                     registry,
                                                     app,
                                                     process_url,
                                                     app_participant):
        path = process_url + '/proposal_0000000/comments'
        resp = _post_comment_item(app_participant, path=path)
        assert resp.status_code == 200

    def test_participate_participant_creates_polarization(self,
                                                     registry,
                                                     app,
                                                     process_url,
                                                     app_participant):
        path = process_url + '/proposal_0000000/relations'
        resp = _post_polarization_item(app_participant, path=path)
        assert resp.status_code == 200
