from pyramid import testing
from unittest.mock import Mock
from pytest import fixture


class TestDeleteStaleLoginData:

    def call_fut(self, *args):
        from .ad_delete_stale_login_data import delete_stale_login_data
        return delete_stale_login_data(*args)

    @fixture
    def mock_delete_resets(self, monkeypatch):
        from adhocracy_core.resources.principal import delete_password_resets
        from . import ad_delete_stale_login_data
        mock = Mock(spec=delete_password_resets)
        monkeypatch.setattr(ad_delete_stale_login_data, 'delete_password_resets',
                            mock)
        return mock

    @fixture
    def mock_delete_users(self, monkeypatch):
        from adhocracy_core.resources.principal import delete_not_activated_users
        from . import ad_delete_stale_login_data
        mock = Mock(spec=delete_not_activated_users)
        monkeypatch.setattr(ad_delete_stale_login_data, 'delete_not_activated_users',
                            mock)
        return mock

    @fixture
    def mock_token_manger(self, monkeypatch):
        from adhocracy_core.authentication import TokenMangerAnnotationStorage
        from . import ad_delete_stale_login_data
        mock = Mock(spec=TokenMangerAnnotationStorage)
        monkeypatch.setattr(ad_delete_stale_login_data, 'get_tokenmanager',
                            lambda x: mock)
        return mock

    @fixture
    def mock_auth_policy(self, registry):
        from adhocracy_core.authentication import TokenHeaderAuthenticationPolicy
        mock = Mock(spec=TokenHeaderAuthenticationPolicy)
        mock.timeout = 0
        registry.queryUtility = lambda x: mock
        return mock

    def test_delete_stale_users(
            self, context, request_, mock_delete_users, mock_delete_resets):
        self.call_fut(context, request_, 30, 10)
        assert request_.root == context
        mock_delete_users.assert_called_with(request_, 30)

    def test_delete_stale_resets(
            self, context, request_, mock_delete_resets, mock_delete_users):
        self.call_fut(context, request_, 30, 10)
        mock_delete_resets.assert_called_with(request_, 10)
