from pytest import fixture
from unittest.mock import Mock
import unittest
from pyramid import testing

class TestAddResource:

    def call_fut(self, *args):
        from .testing import add_resources
        add_resources(*args)

    @fixture
    def mock_import_resources(self, monkeypatch):
        from adhocracy_core import scripts
        mock = Mock(spec=scripts.import_resources)
        monkeypatch.setattr(scripts, 'import_resources', mock)
        return mock

    @fixture
    def mock_get_root(self, monkeypatch):
        from adhocracy_core import utils
        mock = Mock(spec=utils.get_root)
        monkeypatch.setattr(utils, 'get_root', mock)
        return mock

    @fixture
    def mock_transaction_commit(self, monkeypatch):
        import transaction
        mock = Mock(spec=transaction.commit)
        monkeypatch.setattr(transaction, 'commit', mock)
        return mock

    def test_add_resources(self,
                           app,
                           mock_import_resources,
                           mock_get_root,
                           mock_transaction_commit):
        filename = "/tmp/dummy.json"
        dummy_root = testing.DummyResource()
        mock_get_root.return_value = dummy_root
        self.call_fut(app, filename)
        assert mock_get_root.called
        mock_import_resources.assert_called_once_with(dummy_root,
                                                      app.registry,
                                                      filename)
        assert mock_transaction_commit.called
