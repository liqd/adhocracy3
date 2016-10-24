import pytest

from pyramid import testing

from unittest.mock import Mock
from pytest import fixture


@fixture
def mock_auditlog(mocker):
    return mocker.patch('adhocracy_core.auditing.AuditLog',
                        autospec=True)


class TestAuditlog:

    @fixture
    def inst(self):
        from . import AuditLog
        return AuditLog()

    def test_create(self, inst):
        from BTrees.OOBTree import OOBTree
        assert isinstance(inst, OOBTree)

    def test_add_basic_activity(self, inst, activity):
        import datetime
        from adhocracy_core.interfaces import SerializedActivity
        object = testing.DummyResource(__name__='object')
        published= datetime.datetime.utcnow()
        activity = activity._replace(type='create',
                                     object=object,
                                     published=published,
                                     )
        inst.add(activity)
        key, value = inst.items()[0]
        assert isinstance(value, SerializedActivity)
        assert key == published
        assert value.type == 'create'
        assert value.object_path == 'object'
        assert value.sheet_data == []
        assert value.target_path == ''

    def test_add_basic_activity_with_subject(self, inst, activity):
        import datetime
        from adhocracy_core.interfaces import SerializedActivity
        subject = testing.DummyResource(__name__='subject')
        object = testing.DummyResource(__name__='object')
        published= datetime.datetime.utcnow()
        activity = activity._replace(subject=subject,
                                     type='create',
                                     object=object,
                                     published=published,
                                     )
        inst.add(activity)
        key, value = inst.items()[0]
        assert value.subject_path == 'subject'

    def test_add_activity_with_target_and_sheet_data(self, inst, activity):
        import datetime
        subject = testing.DummyResource(__name__='subject')
        object = testing.DummyResource(__name__='object')
        target = testing.DummyResource(__name__='target')
        published= datetime.datetime.utcnow()
        activity = activity._replace(subject=subject,
                                     type='create',
                                     object=object,
                                     target=target,
                                     sheet_data=[{'y': 'z'}],
                                     published=published
                                     )
        inst.add(activity)
        key, value = inst.items()[0]
        assert value.sheet_data == [{'y': 'z'}]
        assert value.target_path == 'target'


def test_get_auditlog(context, mocker):
    from . import get_auditlog
    mock = mocker.patch('substanced.util.get_auditlog', autospec=True)
    get_auditlog(context)
    assert mock.called


class TestSetAuditlog:

    def call_fut(self, ctx):
        from . import set_auditlog
        return set_auditlog(ctx)

    @fixture
    def context(self):
        context = Mock()
        mocked_conn = Mock()
        mocked_auditconn = Mock()
        mocked_auditconn.root.return_value = {'auditlog': Mock()}
        mocked_conn.get_connection.return_value = mocked_auditconn
        context._p_jar = mocked_conn
        return context

    @fixture
    def context_emptyroot(self, context):
        context._p_jar.get_connection.return_value.root.return_value = {}
        return context

    def test_set_auditlog_no_audit_connection(self, context):
        from . import get_auditlog
        context._p_jar.get_connection = Mock(name='method',
                                             side_effect=KeyError('audit'))
        self.call_fut(context)
        assert get_auditlog(context) is None

    def test_set_auditlog_previous_auditlog(self, context, mock_auditlog):
        self.call_fut(context)
        assert mock_auditlog.called is False

    def test_set_auditlog_no_previous_auditlog(self, context_emptyroot,
                                               mock_auditlog):
        self.call_fut(context_emptyroot)
        assert mock_auditlog.called is True


class TestAddToAuditLog:

    def call_fut(self, *args):
        from . import add_to_auditlog
        return add_to_auditlog(*args)

    @fixture
    def mock_auditlog(self, mocker, mock_auditlog):
        mocker.patch('adhocracy_core.auditing.get_auditlog',
                     autospec=True,
                     return_value=mock_auditlog)
        return mock_auditlog

    def test_ignore_if_no_auditlog(self, activity, mocker, request_):
        mocker.patch('adhocracy_core.auditing.get_auditlog', return_value=None)
        assert self.call_fut([activity], request_) is None

    def test_add(self, activity, mock_auditlog, request_):
        self.call_fut([activity], request_)
        mock_auditlog.add.assert_called_with(activity)

    def test_add_sends_added_event(self, activity, config, mock_auditlog,
                                   request_):
        from adhocracy_core.testing import create_event_listener
        from adhocracy_core.interfaces import IActivitiesAddedToAuditLog
        added_listener = create_event_listener(config,
                                               IActivitiesAddedToAuditLog)
        self.call_fut([activity], request_)
        event = added_listener[0]
        assert event.object == mock_auditlog
        assert event.activities == [activity]
