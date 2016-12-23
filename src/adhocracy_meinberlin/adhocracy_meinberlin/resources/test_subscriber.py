import datetime

from unittest.mock import Mock
from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(integration):
    integration.include('pyramid_mailer.testing')
    integration.include('pyramid_mako')
    integration.include('adhocracy_core.messaging')
    integration.registry['config'].adhocracy.use_mail_queue = False
    return integration


@mark.usefixtures('integration')
class TestBplanSubmissionConfirmationEmailSubscriber:

    @fixture
    def process_settings_appstruct(self):
        return {'plan_number': '112233-ba',
                'participation_kind': 'öffentliche Auslegung'}

    @fixture
    def process_private_settings_appstruct(self):
        return {'office_worker_email': 'officeworkername@example.org'}

    @fixture
    def process_private_settings_no_email_appstruct(self):
        return {'office_worker_email': None}

    @fixture
    def workflow_state_data_appstruct(self):
        return {'state_data': [
                {'name': 'participate',
                 'description': '',
                 'start_date': datetime.date(2015, 5, 5)},
                {'name': 'closed',
                 'description': '',
                 'start_date': datetime.date(2015, 6, 11)}
        ]}

    def _make_process(self,
                      registry,
                      context,
                      process_settings_appstruct,
                      process_private_settings_appstruct,
                      workflow_state_data_appstruct):
        from adhocracy_meinberlin import resources
        import adhocracy_meinberlin.sheets.bplan
        import adhocracy_core.sheets.name
        bplan_appstructs = {adhocracy_core.sheets.name.IName.__identifier__:
                            {'name': 'bplan'},
                            adhocracy_core.sheets.title.ITitle.__identifier__:
                            {'title': 'Sample BPlan process'},
                            adhocracy_meinberlin.sheets.bplan.IProcessSettings.__identifier__:
                            process_settings_appstruct,
                            adhocracy_meinberlin.sheets.bplan.IProcessPrivateSettings.__identifier__:
                            process_private_settings_appstruct,
                            adhocracy_core.sheets.workflow.IWorkflowAssignment.__identifier__:
                            workflow_state_data_appstruct}
        process = registry.content.create(resources.bplan.IProcess.__identifier__,
                                          parent=context,
                                          appstructs=bplan_appstructs)
        return context

    @fixture
    def context(self,
                registry,
                pool_with_catalogs,
                process_settings_appstruct,
                process_private_settings_appstruct,
                workflow_state_data_appstruct):
        return self._make_process(registry,
                                  pool_with_catalogs,
                                  process_settings_appstruct,
                                  process_private_settings_appstruct,
                                  workflow_state_data_appstruct)

    @fixture
    def context_no_office_worker(self,
                                 registry,
                                 pool_with_catalogs,
                                 process_settings_appstruct,
                                 process_private_settings_no_email_appstruct,
                                 workflow_state_data_appstruct):
        return self._make_process(registry,
                                  pool_with_catalogs,
                                  process_settings_appstruct,
                                  process_private_settings_no_email_appstruct,
                                  workflow_state_data_appstruct)

    @fixture
    def appstructs(self):
        from adhocracy_meinberlin import sheets
        return {sheets.bplan.IProposal.__identifier__:
                {'name': 'Laura Muster',
                 'email': 'user@example.com',
                 'street_number': '1234',
                 'postal_code_city': '10000, Berlin',
                 'statement': 'BplanStatement1\nBplanStatement2'
                }}

    def make_bplan_proposal(self, context, registry, appstructs):
        from adhocracy_meinberlin import resources
        proposal_item = registry.content.create(resources.bplan.IProposal.__identifier__,
                                                parent=context['bplan'])
        inst = registry.content.create(resources.bplan.IProposalVersion.__identifier__,
                                       parent=proposal_item,
                                       appstructs=appstructs)
        return inst

    @fixture
    def mailer(self, registry):
        return registry.messenger.mailer

    def test_email_sent_to_user(self, registry, context, mailer, appstructs):
        mailer.outbox = []
        self.make_bplan_proposal(context, registry, appstructs)
        assert len(mailer.outbox) == 2
        msg_user = mailer.outbox[0]
        assert 'user@example.com' in msg_user.recipients
        assert 'Ihre Stellungnahme zum Bebauungsplan 112233-ba, öffentliche Auslegung' \
            ' von 05/05/2015 - 11/06/2015.'  == msg_user.subject
        assert 'Vielen Dank' in msg_user.body
        assert 'Laura Muster' in msg_user.body
        assert 'user@example.com' in msg_user.body
        assert '1234' in msg_user.body
        assert '10000, Berlin' in msg_user.body
        assert 'BplanStatement1' in msg_user.body
        assert 'BplanStatement2' in msg_user.body
        assert '112233-ba' in msg_user.body
        assert '05/05/2015' in msg_user.body
        assert '11/06/2015' in msg_user.body
        assert 'Ihre Stellungnahme zum Bebauungsplan 112233-ba, öffentliche Auslegung' \
            ' von 05/05/2015 - 11/06/2015.' in msg_user.body

    def test_email_sent_to_office_worker(self, registry, context, mailer, appstructs):
        mailer.outbox = []
        self.make_bplan_proposal(context, registry, appstructs)
        assert len(mailer.outbox) == 2
        msg_officeworker = mailer.outbox[1]
        assert 'officeworkername@example.org' in msg_officeworker.recipients
        assert 'Vielen Dank' in msg_officeworker.body
        assert 'Laura Muster' in msg_officeworker.body
        assert 'user@example.com' in msg_officeworker.body
        assert '1234' in msg_officeworker.body
        assert '10000, Berlin' in msg_officeworker.body
        assert 'BplanStatement1' in msg_officeworker.body
        assert 'BplanStatement2' in msg_officeworker.body

    def test_do_not_send_email_if_office_work_not_defined(self,
                                                          registry,
                                                          context_no_office_worker,
                                                          mailer,
                                                          appstructs):
        self.make_bplan_proposal(context_no_office_worker, registry, appstructs)
        assert len(mailer.outbox) == 0
