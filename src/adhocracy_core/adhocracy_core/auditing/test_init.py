import pytest

from pyramid import testing

from unittest.mock import Mock
from pytest import fixture
from pytest import mark
from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import VisibilityChange


@fixture
def integration(integration):
    integration.include('adhocracy_core.changelog')


@fixture
def registry(registry_with_content):
    return registry_with_content


@fixture
def mock_auditlog(mocker):
    return mocker.patch('adhocracy_core.auditing.AuditLog',
                        autospec=True)


@fixture
def mock_generate_activity_name(mocker):
    return mocker.patch('adhocracy_core.auditing.generate_activity_name',
                        autospec=True,
                        return_value='Activity Name')


@mark.usefixtures('mock_generate_activity_name')
class TestUpdateAuditlogCallback:

    def call_fut(self, *args):
        from . import update_auditlog_callback
        return update_auditlog_callback(*args)

    @fixture
    def request_(self,  request_, registry, changelog):
        request_.registry = registry
        request_.registry.changelog = changelog
        return request_

    @fixture
    def item(self, item, version):
        item['versions'] = testing.DummyResource()
        item['versions']['version'] = version
        return item

    @fixture()
    def parent(self, context):
        parent = testing.DummyResource()
        parent['child'] = context
        return parent

    @fixture
    def add_to(self, mocker):
        return mocker.patch('adhocracy_core.auditing.add_to_auditlog')

    def test_ignore_if_empty_changelog(self, request_, mocker):
        add_to = mocker.patch('adhocracy_core.auditing.add_to_auditlog')
        self.call_fut(request_, None)
        assert add_to.call_args[0][0] == []
        assert add_to.call_args[0][1] is request_

    def test_ignore_if_no_real_change(self, request_, add_to, changelog,
                                      context):
        changelog['/nup'] = changelog['']._replace(last_version=context,
                                                   followed_by=context,
                                                   changed_descendants=True,
                                                   changed_backrefs=False,
                                                   )
        self.call_fut(request_, None)
        assert add_to.call_args[0][0] == []

    def test_add_add_activity_if_created(self, request_, add_to, changelog,
                                          context, parent):
        from adhocracy_core.interfaces import ActivityType
        changelog['/resource'] = changelog['']._replace(created=True,
                                                        resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.type == ActivityType.add
        assert added_activity.object == context
        assert added_activity.target == parent

    def test_add_update_activity_if_modified(self, request_, add_to, changelog,
                                             context):
        from adhocracy_core.interfaces import ActivityType
        changelog['/resource']  = changelog['']._replace(modified=True,
                                                         resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.type == ActivityType.update
        assert added_activity.object == context

    def test_add_update_activity_if_version_created(self, request_, add_to,
                                                    changelog, version, item):
        from adhocracy_core.interfaces import ActivityType
        changelog['/resource'] = changelog['']._replace(created=True,
                                                        resource=version)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.type == ActivityType.update
        assert added_activity.target == item

    def test_add_remove_activity_if_concealed(self, request_, add_to, changelog,
                                              context, parent):
        """Concealed == hidden or removed."""
        from adhocracy_core.interfaces import ActivityType
        from adhocracy_core.interfaces import VisibilityChange
        changelog['/resource']  = changelog[''].\
            _replace(visibility=VisibilityChange.concealed, resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.type == ActivityType.remove
        assert added_activity.target == parent

    def test_add_sheet_data_if_created(self, request_, add_to, changelog,
                                       context, mock_sheet, registry):
        registry.content.get_sheets_create.return_value = [mock_sheet]
        changelog['/resource'] = changelog['']._replace(created=True,
                                                        resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        registry.content.get_sheets_create.assert_called_with(context)
        assert added_activity.sheet_data == [{mock_sheet.meta.isheet:
                                              mock_sheet.serialize()}]

    def test_add_sheet_data_if_modified(self, request_, add_to, changelog,
                                        context, mock_sheet, registry):
        registry.content.get_sheets_edit.return_value = [mock_sheet]
        changelog['/resource'] = changelog['']._replace(modified=True,
                                                        resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        registry.content.get_sheets_edit.assert_called_with(context)
        assert added_activity.sheet_data == [{mock_sheet.meta.isheet:
                                              mock_sheet.serialize()}]

    def test_add_name(self, request_, add_to, changelog, context,
                      mock_generate_activity_name):
        changelog['/resource'] = changelog['']._replace(modified=True,
                                                        resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.name == mock_generate_activity_name.return_value


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
        subject = testing.DummyResource(__name__='subject')
        object = testing.DummyResource(__name__='object')
        activity = activity._replace(subject=subject,
                                     type='create',
                                     object=object,
                                     )
        inst.add(activity)
        key, value = inst.items()[0]
        assert isinstance(value, SerializedActivity)
        assert isinstance(key, datetime.datetime)
        assert value.subject_path == 'subject'
        assert value.type == 'create'
        assert value.object_path == 'object'
        assert value.sheet_data == []
        assert value.target_path == ''

    def test_add_activity_with_target_and_sheet_data(self, inst, activity):
        subject = testing.DummyResource(__name__='subject')
        object = testing.DummyResource(__name__='object')
        target = testing.DummyResource(__name__='target')
        activity = activity._replace(subject=subject,
                                     type='create',
                                     object=object,
                                     target=target,
                                     sheet_data=[{'y': 'z'}],
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


@fixture
def get_title(mocker):
    return mocker.patch('adhocracy_core.auditing._get_title',
                        autospec=True,
                        return_value='title')


@fixture
def get_subject_name(mocker):
    return mocker.patch('adhocracy_core.auditing._get_subject_name',
                        autospec=True,
                        return_value='user name')


@fixture
def get_resource_type(mocker):
    return mocker.patch('adhocracy_core.auditing._get_type_name',
                        autospec=True,
                        return_value='type name')


@mark.usefixtures('get_subject_name', 'get_resource_type', 'get_title')
class TestGenerateActivityName:

    def call_fut(self, *args):
        from . import generate_activity_name
        return generate_activity_name(*args)

    def test_create_translation_with_mapping(
        self, activity, registry, get_subject_name, get_resource_type,
        get_title):
        from pyramid.i18n import TranslationString
        name = self.call_fut(activity, registry)
        get_subject_name.assert_called_with(activity.subject, registry)
        get_resource_type.assert_called_with(activity.subject, registry)
        get_title.assert_called_with(activity.subject, registry)
        assert isinstance(name, TranslationString)
        assert name.mapping == {'subject_name': 'user name',
                                'object_type_name': 'type name',
                                'target_title': 'title',
                                }

    def test_create_missing_translation_if_no_type(self, activity, registry):
        activity = activity._replace(type=None)
        name = self.call_fut(activity, registry)
        assert name == 'activity_missing'

    def test_create_add_translation_if_add_activity(self, activity, registry):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.add)
        name = self.call_fut(activity, registry)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_name_add'

    def test_create_add_translation_if_remove_activity(self, activity,
                                                       registry):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.remove)
        name = self.call_fut(activity, registry)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_name_remove'

    def test_create_add_translation_if_update_activity(self, activity,
                                                       registry):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.update)
        name = self.call_fut(activity, registry)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_name_update'


@mark.usefixtures('get_subject_name', 'get_resource_type', 'get_title')
class TestGenerateActivityDescription:

    def call_fut(self, *args):
        from . import generate_activity_description
        return generate_activity_description(*args)

    def test_create_translation_with_mapping(
        self, activity, registry, get_subject_name, get_resource_type,
        get_title):
        from pyramid.i18n import TranslationString
        name = self.call_fut(activity, registry)
        get_subject_name.assert_called_with(activity.subject, registry)
        get_resource_type.assert_called_with(activity.subject, registry)
        get_title.assert_called_with(activity.subject, registry)
        assert isinstance(name, TranslationString)
        assert name.mapping == {'subject_name': 'user name',
                                'object_title': 'title',
                                'object_type_name': 'type name',
                                'target_title': 'title',
                                'target_type_name': 'type name',
                                }

    def test_create_missing_translation_if_no_type(self, activity, registry):
        activity = activity._replace(type=None)
        name = self.call_fut(activity, registry)
        assert name == 'activity_missing'

    def test_create_add_translation_if_add_activity(self, activity, registry):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.add)
        name = self.call_fut(activity, registry)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_description_add'

    def test_create_add_translation_if_remove_activity(self, activity, registry):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.remove)
        name = self.call_fut(activity, registry)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_description_remove'

    def test_create_add_translation_if_update_activity(self, activity, registry):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.update)
        name = self.call_fut(activity, registry)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_description_update'


def test_get_subject_name_return_user_name(context, registry):
    from adhocracy_core.sheets.principal import IUserBasic
    from . import _get_subject_name
    registry.content.get_sheet_field = Mock(return_value='user_name')
    assert _get_subject_name(context, registry) == 'user_name'
    registry.content.get_sheet_field.assert_called_with(context, IUserBasic,
                                                        'name')


def test_get_subject_name_return_application_if_no_user(registry):
    """See https://www.w3.org/TR/activitystreams-vocabulary/#actor-types """
    from . import _get_subject_name
    assert _get_subject_name(None, registry) == 'Application'


def test_get_type_name_return_content_name(context, registry, resource_meta):
    from . import _get_type_name
    registry.content.resources_meta[resource_meta.iresource] =\
        resource_meta._replace(content_name='Resource')
    assert _get_type_name(context, registry) == 'Resource'


def test_get_type_name_return_empty_if_none(registry):
    from . import _get_type_name
    assert _get_type_name(None, registry) == ''


def test_get_title_return_title(registry):
    from adhocracy_core.sheets.title import ITitle
    from . import _get_title
    context = testing.DummyResource(__provides__=ITitle)
    registry.content.get_sheet_field = Mock(return_value='title')
    assert _get_title(context, registry) == 'title'
    registry.content.get_sheet_field.assert_called_with(context, ITitle,
                                                        'title')


def test_get_title_return_empty_if_missing_sheet(registry):
    from . import _get_title
    context = testing.DummyResource()
    assert _get_title(context, registry) == ''


def test_get_title_return_empty_string_if_none(registry):
    from . import _get_title
    assert _get_title(None, registry) == ''

