from datetime import datetime
from unittest.mock import Mock
from pytest import fixture


class TestAuditlog:

    def call_fut(self, *args, **kwargs):
        from .ad_auditlog import auditlog_show
        return auditlog_show(*args, **kwargs)

    @fixture
    def mock_timestamp(self):
        return datetime(2016,1,1)

    @fixture
    def mock_auditlog_entries(self, mocker, mock_timestamp):
        mock_auditlog_entries = Mock()
        mock_auditlog_entry1 = Mock()
        mock_auditlog_entry1.object_path = '/path1/x'
        mock_auditlog_entry2 = Mock()
        mock_auditlog_entry2.object_path = '/path2'
        mock_auditlog_entries.items.return_value = [
            (mock_timestamp, mock_auditlog_entry1),
            (mock_timestamp, mock_auditlog_entry2)]
        return mock_auditlog_entries

    @fixture
    def mock_auditlog(self,  mocker, mock_auditlog_entries):
        mock = mocker.patch(
            'adhocracy_core.scripts.ad_auditlog.'
            'get_auditlog',
            return_value = mock_auditlog_entries)
        return mock

    @fixture
    def mock_print(self, mocker):
        mock = mocker.patch(
            'adhocracy_core.scripts.ad_auditlog.'
            'print',
            create = True)
        return mock

    def test_auditlog_show(self, context, mock_auditlog,
            mock_auditlog_entries, mock_timestamp, mock_print):
        self.call_fut(context)
        print_str1 = '{}: {}'.format(
            mock_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            mock_auditlog_entries.items()[0][1])
        mock_print.assert_any_call(print_str1)
        print_str2 = '{}: {}'.format(
            mock_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            mock_auditlog_entries.items()[1][1])
        mock_print.assert_any_call(print_str2)

    def test_auditlog_filter_path(self, context, mock_auditlog,
            mock_auditlog_entries, mock_timestamp, mock_print):
        self.call_fut(context, path='/path1')
        print_str = '{}: {}'.format(
            mock_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            mock_auditlog_entries.items()[0][1])
        mock_print.assert_called_with(print_str)
