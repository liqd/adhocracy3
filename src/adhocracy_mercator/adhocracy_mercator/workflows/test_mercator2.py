from pytest import mark
from pytest import fixture
from webtest import TestResponse

from adhocracy_core.testing import add_resources
from adhocracy_core.testing import do_transition_to


def _post_proposal(app_user, path='/') -> TestResponse:
    from adhocracy_mercator.resources.mercator2 import IMercatorProposal
    resp = app_user.post_resource(path, IMercatorProposal, {})
    return resp


def _post_comment_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.comment import IComment
    resp = app_user.post_resource(path, IComment, {})
    return resp


@mark.functional
@mark.usefixtures('log')
class TestMercator2:

    @fixture
    def process_url(self):
        return '/organisation/advocate-europe2'

    @fixture
    def proposal0_url(self):
        return '/organisation/advocate-europe2/proposal_0000000'

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

    def test_participate_participant_creates_proposal(self,
                                                      process_url,
                                                      app_participant):
        resp = _post_proposal(app_participant, path=process_url)
        assert resp.status_code == 200

    def test_participate_participant_can_read_extrafunding(self,
                                                           app_participant,
                                                           proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IExtraFunding
        resp = app_participant.get(proposal0_url)
        data = resp.json_body['data']
        assert IExtraFunding.__identifier__ in data

    def test_participate_participant2_cannot_read_extrafunding(self,
                                                               app_participant2,
                                                               proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IExtraFunding
        resp = app_participant2.get(proposal0_url)
        data = resp.json_body['data']
        assert IExtraFunding.__identifier__ not in data

    def test_participate_participant_can_edit_topic(self,
                                                    app_participant,
                                                    proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import ITopic
        resp = app_participant.options(proposal0_url)
        data = resp.json_body['PUT']['request_body']['data']
        assert ITopic.__identifier__ in data

    def test_participate_participant_creates_comment(self,
                                                     app_participant,
                                                     proposal0_url):
        path = proposal0_url +  '/comments'
        resp = _post_comment_item(app_participant, path=path)
        assert resp.status_code == 200

    def test_participate_participant_cannot_update_winnerinfo(self,
                                                              app_participant,
                                                              proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IWinnerInfo
        resp = app_participant.options(proposal0_url)
        data = resp.json_body['PUT']['request_body']['data']
        assert IWinnerInfo not in data

    def test_participate_participant_can_assign_badge(self,
                                                 app_participant,
                                                 proposal0_url):
        from adhocracy_core.resources.badge import IBadgeAssignment
        url = proposal0_url + '/badge_assignments'
        postable_types = app_participant.get_postable_types(url)
        assert IBadgeAssignment in postable_types

    def test_set_evaluate_state(self, process_url, app_admin):
        resp = do_transition_to(app_admin,
                                process_url,
                                'evaluate')
        assert resp.status_code == 200

    def test_evaluate_participant_cannot_creates_proposal(self,
                                                          process_url,
                                                          app_participant):
        from adhocracy_mercator.resources.mercator2 import IMercatorProposal
        postable_types = app_participant.get_postable_types(process_url)
        assert IMercatorProposal not in postable_types

    def test_evaluate_participant_cannot_comment(self,
                                                 app_participant,
                                                 proposal0_url):
        from adhocracy_core.resources.comment import ICommentVersion
        url = proposal0_url + '/comments'
        postable_types = app_participant.get_postable_types(url)
        assert ICommentVersion not in postable_types

    def test_evaluate_participant_cannot_edit_topic(self,
                                                    app_participant,
                                                    proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import ITopic
        resp = app_participant.options(proposal0_url)
        assert 'PUT' not in resp.json_body

    def test_evaluate_moderator_can_update_winnerinfo(self,
                                                      app_moderator,
                                                      proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IWinnerInfo
        resp = app_moderator.options(proposal0_url)
        data = resp.json_body['PUT']['request_body']['data']
        assert IWinnerInfo.__identifier__ in data

    def test_evaluate_participant_cannot_view_winnerinfo(self,
                                                         app_participant,
                                                         proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IWinnerInfo
        resp = app_participant.options(proposal0_url)
        data = resp.json_body['GET']['response_body']['data']
        assert IWinnerInfo.__identifier__ not in data

    def test_evaluate_moderator_can_assign_badge(self,
                                                 app_moderator,
                                                 proposal0_url):
        from adhocracy_core.resources.badge import IBadgeAssignment
        url = proposal0_url + '/badge_assignments'
        postable_types = app_moderator.get_postable_types(url)
        assert IBadgeAssignment in postable_types

    def test_set_result_state(self, process_url, app_admin):
        resp = do_transition_to(app_admin, process_url, 'result')
        assert resp.status_code == 200

    def test_result_participant_can_view_winnerinfo(self,
                                                    app_participant,
                                                    proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IWinnerInfo
        resp = app_participant.options(proposal0_url)
        data = resp.json_body['GET']['response_body']['data']
        assert IWinnerInfo.__identifier__ in data

    def test_result_participant_cannot_creates_proposal(self,
                                                        process_url,
                                                        app_participant):
        from adhocracy_mercator.resources.mercator2 import IMercatorProposal
        postable_types = app_participant.get_postable_types(process_url)
        assert IMercatorProposal not in postable_types

    def test_result_participant_cannot_comment(self,
                                               app_participant,
                                               proposal0_url):
        from adhocracy_core.resources.comment import ICommentVersion
        url = proposal0_url + '/comments'
        postable_types = app_participant.get_postable_types(url)
        assert ICommentVersion not in postable_types

    def test_result_participant_can_edit_topic(self,
                                               app_participant,
                                               proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import ITopic
        resp = app_participant.options(proposal0_url)
        data = resp.json_body['PUT']['request_body']['data']
        assert ITopic.__identifier__ in data

    # partners are a subresources
    def test_result_participant_can_edit_partners(self,
                                                  app_participant,
                                                  proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IPartners
        resp = app_participant.options(proposal0_url)
        sheets = set()
        for data in resp.json_body['POST']['request_body']:
            sheets.update(data['data'].keys())
        assert IPartners.__identifier__ in sheets

    def test_result_participant_can_create_logbook(self,
                                                   app_participant,
                                                   proposal0_url):
        from adhocracy_core.resources.document import IDocument
        postable_types = app_participant.get_postable_types(proposal0_url +
                                                            '/logbook')
        assert IDocument in postable_types

    def test_set_closed_state(self, process_url, app_admin):
        resp = do_transition_to(app_admin,
                                process_url,
                                'closed')
        assert resp.status_code == 200

    def test_closed_participant_cannot_edit_topic(self,
                                                  app_participant,
                                                  proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import ITopic
        resp = app_participant.options(proposal0_url)
        assert 'PUT' not in resp.json_body
