from pyramid import testing
from pytest import fixture
from pytest import mark


class TestAlexanderplatzWorkflow:

    def get_acl(self, state):
        from adhocracy_core.schema import ACM
        from adhocracy_core.authorization import acm_to_acl
        from adhocracy_core.renderers import YAMLToPython
        render = YAMLToPython({})
        meta = render({},
                      {'renderer_name':
                       'adhocracy_meinberlin.workflows:alexanderplatz.yaml'})
        acm = ACM().deserialize(meta['states'][state]['acm'])
        acl = acm_to_acl(acm)
        return acl

    def test_announce_moderator_can_view_document(self):
        acl = self.get_acl('announce')
        index_allow = acl.index(('Allow', 'role:moderator', 'view'))
        index_deny = acl.index(('Deny', 'role:participant', 'view'))
        assert index_allow < index_deny

    def test_announce_moderator_can_create_edit_any_document(self):
        acl = self.get_acl('announce')
        assert ('Allow', 'role:moderator', 'create_document') in acl
        assert ('Allow', 'role:moderator', 'edit') in acl

    def test_participate_moderator_can_add_edit_any_document(self):
        acl = self.get_acl('participate')
        assert ('Allow', 'role:moderator', 'create_document') in acl
        assert ('Allow', 'role:moderator', 'edit') in acl

    def test_participate_participant_can_create_proposal(self):
        acl = self.get_acl('participate')
        assert ('Allow', 'role:participant', 'create_proposal') in acl

    def test_participate_participant_can_create_comment(self):
        acl = self.get_acl('participate')
        assert ('Allow', 'role:participant', 'create_comment') in acl

    def test_participate_participant_cannot_create_edit_document(self):
        acl = self.get_acl('participate')
        assert ('Allow', 'role:participant', 'create_document') not in acl
        assert ('Allow', 'role:participant', 'edit') not in acl

    def test_evaluate_moderator_can_create_edit_any_document(self):
        acl = self.get_acl('evaluate')
        assert ('Allow', 'role:moderator', 'create_document') in acl
        assert ('Allow', 'role:moderator', 'edit') in acl

    def test_evaluate_participant_can_create_comment(self):
        acl = self.get_acl('evaluate')
        assert ('Allow', 'role:participant', 'create_comment') in acl

    def test_result_moderator_can_create_edit_any_document(self):
        acl = self.get_acl('result')
        assert ('Allow', 'role:moderator', 'create_document') in acl
        assert ('Allow', 'role:moderator', 'edit') in acl

    def test_result_participant_cannot_create_comment(self):
        acl = self.get_acl('result')
        assert ('Allow', 'role:participant', 'create_comment') not in acl


@mark.usefixtures('integration')
def test_includeme_add_alexanderplatz_workflow(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['alexanderplatz']
    assert isinstance(workflow, AdhocracyACLWorkflow)
