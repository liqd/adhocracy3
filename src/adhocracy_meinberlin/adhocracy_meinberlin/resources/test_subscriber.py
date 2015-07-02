from unittest.mock import Mock
from pyramid import testing
from pytest import fixture
from pytest import mark

def test_set_root_acms(monkeypatch):
    from adhocracy_core.resources.root import root_acm
    from .root import meinberlin_acm
    from .subscriber import set_root_acms
    mock_set_acms = Mock()
    monkeypatch.setattr('adhocracy_meinberlin.resources.subscriber'
                        '.set_acms_for_app_root', mock_set_acms)
    event = Mock()
    set_root_acms(event)
    mock_set_acms.assert_called_with(event.app, (meinberlin_acm, root_acm))

@mark.usefixtures('integration')
class TestBplanSubmissionConfirmationEmailSubscriber:

    @fixture
    def event(self, context, mock_sheet):
        return testing.DummyResource(object=mock_sheet, registry=Mock())

    @fixture
    def registry(self, config):
        config.include('pyramid_mailer.testing')
        config.include('pyramid_mako')
        return config.registry

    @fixture
    def process_settings_appstruct(self, registry, pool_with_catalogs):
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import IPrincipalsService
        import adhocracy_core.sheets.principal
        context = pool_with_catalogs
        registry.content.create(IPrincipalsService.__identifier__,
                                parent=context)
        user_appstructs = {adhocracy_core.sheets.principal.IUserExtended.__identifier__:
                           {'email': 'officeworkername@example.org'}}
        office_worker = registry.content.create(IUser.__identifier__,
                                                appstructs=user_appstructs,
                                                parent=context['principals']['users'])
        return {'office_worker': office_worker,
                'plan_number': '112233',
                'construction_date': '24/09/2015',
                'participation_end_date': '11/06/2015'}


    @fixture
    def process_settings_no_office_worker_appstruct(self, registry, pool_with_catalogs):
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.resources.principal import IPrincipalsService
        import adhocracy_core.sheets.principal
        context = pool_with_catalogs
        registry.content.create(IPrincipalsService.__identifier__,
                                parent=context)
        user_appstructs = {adhocracy_core.sheets.principal.IUserExtended.__identifier__:
                           {'email': 'officeworkername@example.org'}}
        return {'office_worker': None,
                'plan_number': '112233',
                'construction_date': '24/09/2015',
                'participation_end_date': '11/06/2015'}

    def _make_process(self, registry, context, process_settings_appstruct):
        from adhocracy_meinberlin import resources
        import adhocracy_meinberlin.sheets.bplan
        import adhocracy_core.sheets.name
        bplan_appstructs = {adhocracy_core.sheets.name.IName.__identifier__:
                            {'name': 'bplan'},
                            adhocracy_core.sheets.title.ITitle.__identifier__:
                            {'title': 'Sample BPlan process'},
                            adhocracy_meinberlin.sheets.bplan.IProcessSettings.__identifier__:
                            process_settings_appstruct}
        process = registry.content.create(resources.bplan.IProcess.__identifier__,
                                          parent=context,
                                          appstructs=bplan_appstructs)
        return context

    @fixture
    def context(self, registry, pool_with_catalogs, process_settings_appstruct):
        return self._make_process(registry, pool_with_catalogs, process_settings_appstruct)

    @fixture
    def context_no_office_worker(self, registry, pool_with_catalogs,
                                 process_settings_no_office_worker_appstruct):
        return self._make_process(registry, pool_with_catalogs,
                                  process_settings_no_office_worker_appstruct)

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
        from adhocracy_core.sheets.name import IName
        from adhocracy_meinberlin import sheets
        from adhocracy_meinberlin import resources
        proposal_item = registry.content.create(resources.bplan.IProposal.__identifier__,
                                                parent=context['bplan'])
        inst = registry.content.create(resources.bplan.IProposalVersion.__identifier__,
                                       parent=proposal_item,
                                       appstructs=appstructs)
        return inst

    @fixture
    def messenger(self, registry):
        from adhocracy_core.messaging import Messenger
        return Messenger(registry)

    def test_email_sent_to_user(self, registry, context, messenger, appstructs):
        registry.messenger = messenger
        self.make_bplan_proposal(context, registry, appstructs)
        assert len(messenger.mailer.outbox) == 2

        msg_user = messenger.mailer.outbox[0]
        assert 'user@example.com' in msg_user.recipients
        assert 'Bestätigung' in msg_user.subject
        assert 'Vielen Dank' in msg_user.body
        assert 'Laura Muster' in msg_user.body
        assert 'user@example.com' in msg_user.body
        assert '1234' in msg_user.body
        assert '10000, Berlin' in msg_user.body
        assert 'BplanStatement1' in msg_user.body
        assert 'BplanStatement2' in msg_user.body
        assert '112233' in msg_user.body
        assert '24/09/2015' in msg_user.body
        assert '11/06/2015' in msg_user.body

        msg_officeworker = messenger.mailer.outbox[1]
        assert 'officeworkername@example.org' in msg_officeworker.recipients
        assert 'Bestätigung' in msg_officeworker.subject
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
                                                          messenger,
                                                          appstructs):
        registry.messenger = messenger
        self.make_bplan_proposal(context_no_office_worker, registry, appstructs)
        assert len(messenger.mailer.outbox) == 0
