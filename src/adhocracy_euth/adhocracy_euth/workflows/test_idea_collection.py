from pytest import mark
from pytest import fixture
from webtest import TestResponse

from adhocracy_core.testing import add_resources
from adhocracy_core.testing import do_transition_to


def _post_proposal_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.proposal import IProposal
    resp = app_user.post_resource(path, IProposal, {})
    return resp


@mark.functional
class TestIdeaCollection:

    @fixture
    def process_url(self):
        return '/opin/idea_collection'

    @fixture(scope='class')
    def app_router(self, app_settings):
        """Add a `badge_assignment` workflow to badge resources."""
        from adhocracy_core.testing import make_configurator
        from adhocracy_core.resources import add_resource_type_to_registry
        from adhocracy_core.resources.badge import badge_meta
        import adhocracy_euth
        configurator = make_configurator(app_settings, adhocracy_euth)
        core_badge_meta = badge_meta._replace(default_workflow='badge_assignment')
        add_resource_type_to_registry(core_badge_meta, configurator)
        app_router = configurator.make_wsgi_app()
        return app_router

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
        resp = _post_proposal_item(app_participant, path=process_url)
        assert resp.status_code == 200

    def test_participate_participant_can_create_badge(self,
                                                      process_url,
                                                      app_participant,
                                                      app_admin):
        from adhocracy_core.resources.badge import IBadgeAssignment
        url = process_url + '/proposal_0000000/badge_assignments'
        resp = app_participant.options(url)
        badge_assignment = 'adhocracy_core.sheets.badge.IBadgeAssignment'
        post_request_body = resp.json['POST']['request_body']
        assert badge_assignment in post_request_body[0]['data']
        badges = ['http://localhost/opin/idea_collection/badges/categories/culture/',
                  'http://localhost/opin/idea_collection/badges/categories/nature/']
        assert badges[0] in post_request_body[0]['data'][badge_assignment]['badge']
        assert badges[1] in post_request_body[0]['data'][badge_assignment]['badge']
        assert len(post_request_body[0]['data'][badge_assignment]['badge']) is 2
