from pyramid import testing
from pytest import mark
from pytest import fixture
from pytest import mark

from webtest import TestResponse

from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to

@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration

@mark.usefixtures('integration')
def test_includeme_add_stadtforum(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['stadtforum']
    assert isinstance(workflow, AdhocracyACLWorkflow)

@mark.usefixtures('integration')
def test_includeme_add_stadtforum_poll(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['stadtforum_poll']
    assert isinstance(workflow, AdhocracyACLWorkflow)


def _post_poll_item(app_user, path='') -> TestResponse:
    from adhocracy_meinberlin.resources.stadtforum import IPoll
    resp = app_user.post_resource(path, IPoll, {})
    return resp

def _post_comment_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.comment import IComment
    resp = app_user.post_resource(path, IComment, {})
    return resp

def _post_polarization_item(app_user,
                            path='')-> TestResponse:
    from adhocracy_core.resources.relation import IPolarization
    import adhocracy_core.sheets
    resp = app_user.\
    post_resource(path,
                  IPolarization, {})
    return resp

def _post_polarization_version(app_user,
                               path='',
                               object=None,
                               subject=None)-> TestResponse:
    from adhocracy_core.resources.relation import IPolarizationVersion
    import adhocracy_core.sheets
    resp = app_user.\
    post_resource(path,
                  IPolarizationVersion,
                  {adhocracy_core.sheets.relation.IPolarization\
                   .__identifier__:
                   {"object": object,
                    "subject": subject,
                    "position": "pro"
                   }}
    )
    return resp


@mark.functional
class TestStadtForumWorkflow:

    @fixture
    def process_url(self):
        return '/organisation/stadtforum'

    def test_create_resources(self,
                              registry,
                              datadir,
                              process_url,
                              app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app_admin.app_router, json_file)
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

    def test_set_process_participate_state(self, registry, process_url, app_admin):
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

    def test_participate_initiator_creates_proposal(self,
                                                    registry,
                                                    process_url,
                                                    app_initiator):
        resp = _post_poll_item(app_initiator, path=process_url)
        assert resp.status_code == 200

    def test_set_poll_participate_state(self, registry, process_url, app_admin):
        poll_url = process_url + '/poll_0000000'
        resp = app_admin.get(poll_url)
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                poll_url,
                                'announce')
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                poll_url,
                                'participate')
        assert resp.status_code == 200

    def test_participate_participant_creates_comment(self,
                                                     registry,
                                                     process_url,
                                                     app_participant):
        path = process_url + '/poll_0000000/comments'
        resp = _post_comment_item(app_participant, path=path)
        assert resp.status_code == 200

    def test_participate_participant_creates_polarization(self,
                                                          registry,
                                                          process_url,
                                                          app_participant):
        path = process_url + '/poll_0000000/relations'
        resp = _post_polarization_item(app_participant,
                                       path=path,)
        assert resp.status_code == 200

        object_path = process_url + '/poll_0000000/VERSION_0000000'
        subject_path = process_url + \
        '/poll_0000000/comments/comment_0000000/VERSION_0000000'
        polarizationversion_path = path + '/polarization_0000000'

        resp = _post_polarization_version(app_participant,
                                          path=polarizationversion_path,
                                          object=object_path,
                                          subject=subject_path)
        assert resp.status_code == 200

        resp = app_participant.get(subject_path)
        assert resp.status_code == 200
