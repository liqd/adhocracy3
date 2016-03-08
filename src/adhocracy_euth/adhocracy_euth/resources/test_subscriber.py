from pytest import fixture
from unittest.mock import Mock
from pyramid import testing


class TestRemoveParticipantFromAuthenticatedGroup():

    @fixture
    def registry(self, registry_with_content):
        registry_with_content.settings['adhocracy.add_default_group'] = True
        return registry_with_content

    @fixture
    def context(self, pool, service):
        from copy import deepcopy
        pool['principals'] = service
        pool['principals']['groups'] = deepcopy(service)
        group = testing.DummyResource()
        pool['principals']['groups']['authenticated'] = group
        return pool

    @fixture
    def context_without_authenticated(self, pool, service):
        from copy import deepcopy
        pool['principals'] = service
        pool['principals']['groups'] = deepcopy(service)
        group = testing.DummyResource()
        return pool

    @fixture
    def mock_group_sheet(self, registry, mock_sheet):
        registry.content.get_sheet.return_value = mock_sheet
        return mock_sheet

    def call_fut(self, event):
        from .subscriber import _remove_participant_from_authenticated_group
        return _remove_participant_from_authenticated_group(event)

    def test_remove_participant_role(self, registry, context, mock_group_sheet):
        event = Mock()
        event.object = context
        event.registry = registry
        mock_group_sheet.get.return_value = {'users': [],
                                             'roles': ['participant']}
        self.call_fut(event)
        mock_group_sheet.set.assert_called_with({'users': [],
                                                 'roles': []})

    def test_remove_participant_role_no_default_group(
            self,
            registry,
            context_without_authenticated,
            mock_group_sheet):
        event = Mock()
        event.object = context_without_authenticated
        registry.settings['adhocracy.add_default_group'] = False
        event.registry = registry
        mock_group_sheet.get.return_value = {'users': [],
                                             'roles': ['participant']}
        self.call_fut(event)
        assert mock_group_sheet.set.called is False


def test_set_root_acms(monkeypatch):
    from adhocracy_core.resources.root import root_acm
    from .root import euth_acm
    from .subscriber import set_root_acms
    mock_set_acms = Mock()
    monkeypatch.setattr('adhocracy_euth.resources.subscriber'
                        '.set_acms_for_app_root', mock_set_acms)
    event = Mock()
    set_root_acms(event)
    mock_set_acms.assert_called_with(event.app, (euth_acm, root_acm))
