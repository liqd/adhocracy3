from pytest import fixture
from unittest.mock import Mock
from pyramid import testing


@fixture
def mock_get_root(mocker):
    from . import testing
    mock = mocker.patch.object(testing, 'get_root', AutoSpec=True)
    return mock


@fixture
def mock_transaction_commit(mocker):
    mock = mocker.patch('transaction.commit', AutoSpec=True)
    return mock


@fixture
def mock_run_import_function(mocker):
    mock = mocker.patch('adhocracy_core.utils.testing._run_import_function',
                        AutoSpec=True)
    return mock


def test_import_local_roles(mock_run_import_function, app_router):
        from adhocracy_core.scripts import import_local_roles
        from .testing import add_local_roles
        add_local_roles(app_router, '/tmp/import.json')
        assert mock_run_import_function.call_args[0] ==\
               (import_local_roles, app_router, '/tmp/import.json')


def test_import_resources(mock_run_import_function, app_router):
        from adhocracy_core.scripts import import_resources
        from .testing import add_resources
        add_resources(app_router, '/tmp/import.json')
        assert mock_run_import_function.call_args[0] ==\
               (import_resources, app_router, '/tmp/import.json')


class TestRunImportFunction:

    def call_fut(self, *args):
        from .testing import _run_import_function
        _run_import_function(*args)

    def test_run_import_function(self,
                                 app_router,
                                 mock_get_root,
                                 mock_transaction_commit):
        filename = "/tmp/dummy.json"
        mock_import_func = Mock()
        dummy_root = testing.DummyResource()
        dummy_closer = Mock()
        mock_get_root.return_value = (dummy_root, dummy_closer)
        self.call_fut(mock_import_func, app_router, filename)
        assert mock_get_root.called
        mock_import_func.assert_called_once_with(dummy_root,
                                                 app_router.registry,
                                                 filename)
        assert dummy_closer.called
        assert mock_transaction_commit.called

