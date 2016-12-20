from pyramid import testing
from pytest import fixture
from pytest import mark
from webtest import TestResponse

from adhocracy_core.testing import add_resources
from adhocracy_core.testing import do_transition_to


@fixture(scope='class')
def app_anonymous(app_anonymous):
    app_anonymous.base_path = '/organisation'
    return app_anonymous

@fixture(scope='class')
def app_anonymous(app_anonymous):
    app_anonymous.base_path = '/organisation'
    return app_anonymous


@fixture(scope='class')
def app_initiator(app_initiator):
    app_initiator.base_path = '/organisation'
    return app_initiator


@fixture(scope='class')
def app_admin(app_admin):
    app_admin.base_path = '/organisation'
    return app_admin


@mark.usefixtures('integration')
def test_includeme_add_bplan_private_workflow(registry):
    from adhocracy_core.workflows import ACLLocalRolesWorkflow
    workflow = registry.content.workflows['bplan_private']
    assert isinstance(workflow, ACLLocalRolesWorkflow)


@mark.usefixtures('integration')
def test_initiate_bplan_private_workflow(registry, context):
    from adhocracy_core.authorization import get_acl
    workflow = registry.content.workflows['bplan_private']
    assert workflow.state_of(context) is None
    workflow.initialize(context)
    assert workflow.state_of(context) == 'private'
    local_acl = get_acl(context)
    assert ('Deny', 'system.Everyone', 'view') in local_acl


@mark.usefixtures('integration')
def test_includeme_add_bplan_workflow(registry):
    from adhocracy_core.workflows import ACLLocalRolesWorkflow
    workflow = registry.content.workflows['bplan']
    assert isinstance(workflow, ACLLocalRolesWorkflow)


def _post_proposal_item(app_user, path='') -> TestResponse:
    from adhocracy_meinberlin.resources.bplan import IProposal
    resp = app_user.post_resource(path, IProposal, {})
    return resp


def _post_proposal_itemversion(app_user, path='') -> TestResponse:
    from adhocracy_meinberlin.sheets.bplan import IProposal
    from adhocracy_meinberlin.resources.bplan import IProposalVersion
    appstructs = {IProposal.__identifier__: {'name': 'test',
                                             'street_number': '1',
                                             'postal_code_city': '1',
                                             'email': 'test@test.de',
                                             'statement': 'buh',
                                             }}
    resp = app_user.post_resource(path, IProposalVersion, appstructs)
    return resp


@mark.functional
@mark.usefixtures('log')
class TestBPlanWorkflow:

    @fixture(scope='class')
    def app_router(self, app_settings):
        """Set workflow assingment data for bplan process."""
        # FIXME allow to set workflow assignment data with import script
        from adhocracy_core.testing import make_configurator
        from adhocracy_core.resources import add_resource_type_to_registry
        from adhocracy_meinberlin.resources.bplan import process_meta
        import adhocracy_meinberlin
        configurator = make_configurator(app_settings, adhocracy_meinberlin)
        process_meta = process_meta._add(
            after_creation=(self._set_workflow_assignment,))
        add_resource_type_to_registry(process_meta, configurator)
        app_router = configurator.make_wsgi_app()
        return app_router

    @staticmethod
    def _set_workflow_assignment(context, registry, options={}):
        import datetime
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        assigment = registry.content.get_sheet(context, IWorkflowAssignment)
        assigment.set({'state_data': [
            {'name': 'participate','description': '',
             'start_date': datetime.date(2015, 5, 5)},
            {'name': 'closed', 'description': '',
             'start_date': datetime.date(2015, 6, 11)}
        ]})

    def test_create_resources(self,
                              datadir,
                              app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app_admin.app_router, json_file)
        resp = app_admin.get('/bplan')
        assert resp.status_code == 200

    def test_draft_admin_can_view_process(self, app_admin):
        resp = app_admin.get('/bplan')
        assert resp.status_code == 200

    def test_draft_initiator_can_view_process(self, app_initiator):
        resp = app_initiator.get(path='/bplan')
        assert resp.status_code == 200

    def test_draft_anonymous_cannot_view_process(self,
                                                 app_anonymous):
        resp = app_anonymous.get('/bplan')
        assert resp.status_code == 403

    def test_draft_anonymous_cannot_create_proposal(self,
                                                    app_anonymous):
        from adhocracy_meinberlin.resources.bplan import IProposal
        assert IProposal not in app_anonymous.get_postable_types('/bplan')

    def test_change_state_to_announce(self, app_initiator):
        resp = do_transition_to(app_initiator, '/bplan', 'announce')
        assert resp.status_code == 200

    def test_announce_anonymous_can_view_process(self,
                                                 app_anonymous):
        resp = app_anonymous.get('/bplan')
        assert resp.status_code == 200

    def test_anonymous_cannot_create_proposal(self, app_anonymous):
        from adhocracy_meinberlin.resources.bplan import IProposal
        assert IProposal not in app_anonymous.get_postable_types('/bplan')

    def test_change_state_to_participate(self, app_initiator):
        resp = do_transition_to(app_initiator, '/bplan', 'participate')
        assert resp.status_code == 200

    def test_participate_anonymous_creates_proposal(self,
                                                    app_anonymous):
        resp = _post_proposal_item(app_anonymous, path='/bplan')
        assert resp.status_code == 200

    def test_participate_anonymous_edits_proposal_version0(self,
                                                           app_anonymous):
        resp = _post_proposal_itemversion(app_anonymous,
                                          path='/bplan/proposal_0000000')
        assert resp.status_code == 200

    def test_participate_anonymous_gets_notification(self, mailer):
        msg = mailer.outbox[-2]
        assert msg.subject.startswith('Ihre Stellungnahme')
        assert msg.recipients == ['test@test.de']

    def test_participate_office_worker_gets_notification(self,
                                                         mailer):
        msg = mailer.outbox[-1]
        assert msg.subject.startswith('Ihre Stellungnahme')
        assert msg.recipients == ['officeworkername@example.com']

    def test_participate_anonymous_cannot_edit_proposal_version1(self,
                                                                 app_anonymous):
        from adhocracy_meinberlin.resources.bplan import IProposalVersion
        assert IProposalVersion not in app_anonymous.get_postable_types(
            '/bplan/proposal_0000000')

    def test_participate_anonymous_cannot_view_proposal(self,
                                                        app_anonymous):
        resp = app_anonymous.get(path='/bplan/proposal_0000000')
        assert resp.status_code == 403

    def test_participate_initiator_cannot_view_proposal(self,
                                                        app_initiator):
        resp = app_initiator.get(path='/bplan/proposal_0000000')
        assert resp.status_code == 403

    def test_change_state_to_frozen(self, app_initiator):
        resp = do_transition_to(app_initiator, '/bplan', 'closed')
        assert resp.status_code == 200

    def test_closed_anonymous_cannot_create_proposal(self,
                                                     app_anonymous):
        from adhocracy_meinberlin.resources.bplan import IProposal
        assert IProposal not in app_anonymous.get_postable_types('/bplan')

    def test_closed_initiator_cannot_view_proposal(self,
                                                   app_initiator):
        resp = app_initiator.get(path='/bplan/proposal_0000000')
        assert resp.status_code == 403

    def test_closed_anonymous_cannot_view_proposal(self,
                                                     app_anonymous):
        resp = app_anonymous.get('/bplan/proposal_0000000')
        assert resp.status_code == 403
