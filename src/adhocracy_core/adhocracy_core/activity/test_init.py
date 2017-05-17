import pytest

from pyramid import testing

from unittest.mock import Mock
from pytest import fixture
from pytest import mark


@fixture
def integration(integration):
    integration.include('adhocracy_core.changelog')


@fixture
def registry(registry_with_content):
    return registry_with_content


@fixture
def mock_generate_activity_name(mocker):
    return mocker.patch('adhocracy_core.activity.generate_activity_name',
                        autospec=True,
                        return_value='Activity Name')


@mark.usefixtures('mock_generate_activity_name')
class TestUpdateActicityCallback:

    def call_fut(self, *args):
        from . import update_activity_callback
        return update_activity_callback(*args)

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

    @fixture
    def parent(self, context):
        parent = testing.DummyResource()
        parent['child'] = context
        return parent

    @fixture
    def comment(self):
        from adhocracy_core.resources.comment import IComment
        return testing.DummyResource(__provides__=IComment)

    @fixture
    def add_to(self, mocker):
        return mocker.patch('adhocracy_core.activity.add_to_auditlog')

    def test_ignore_if_error_response(self, request_, mocker):
        from pyramid.httpexceptions import HTTPError
        add_to = mocker.patch('adhocracy_core.activity.add_to_auditlog')
        self.call_fut(request_, HTTPError())
        assert not add_to.called

    def test_ignore_if_empty_changelog(self, request_, mocker):
        add_to = mocker.patch('adhocracy_core.activity.add_to_auditlog')
        self.call_fut(request_, None)
        assert not add_to.called

    def test_ignore_if_no_real_change(self, request_, add_to, changelog,
                                      context):
        changelog['/'] = changelog['']._replace(last_version=context,
                                                followed_by=context,
                                                changed_descendants=True,
                                                changed_backrefs=False,
                                                )
        self.call_fut(request_, None)
        assert not add_to.called

    def test_ignore_if_autoupdated_change(self, request_, add_to, changelog,
                                          context):
        changelog['/'] = changelog['']._replace(created=True,
                                                resource=context,
                                                autoupdated=True)
        self.call_fut(request_, None)
        assert not add_to.called

    def test_ignore_if_first_version(
        self, request_, registry, add_to, changelog, version, item):
        changelog['/'] = changelog['']._replace(created=True, resource=version)
        registry.content.get_sheet_field = Mock(return_value=[])
        self.call_fut(request_, None)
        assert not add_to.called

    def test_add_add_activity_if_created(self, request_, add_to, changelog,
                                          context, parent):
        from adhocracy_core.interfaces import ActivityType
        changelog['/'] = changelog['']._replace(created=True, resource=context)
        self.call_fut(request_, None)
        assert add_to.call_args[0][1] == request_
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.type == ActivityType.add
        assert added_activity.object == context
        assert added_activity.target == parent

    def test_add_update_activity_if_modified(self, request_, add_to, changelog,
                                             context):
        from adhocracy_core.interfaces import ActivityType
        changelog['/'] = changelog['']._replace(modified=True, resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.type == ActivityType.update
        assert added_activity.object == context

    def test_add_transition_activity_if_state_modified_and_state_changed(
            self, request_, add_to, changelog, context, mock_sheet):
        from adhocracy_core.interfaces import ActivityType
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        appstructs = {IWorkflowAssignment: {'workflow_state': 'draft'}}
        changelog['/'] = changelog['']._replace(modified=True,
                                                modified_appstructs=appstructs,
                                                resource=context)
        request_.registry.content.get_sheet.return_value = mock_sheet
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.type == ActivityType.transition

    def test_add_update_item_activity_if_version_created(
        self, request_, registry, add_to, changelog, item, version):
        from adhocracy_core.interfaces import ActivityType
        changelog['/'] = changelog['']._replace(created=True, resource=version)
        registry.content.get_sheet_field = Mock()
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.type == ActivityType.update

    def test_add_object(self, request_, add_to, changelog, context):
        changelog['/'] = changelog['']._replace(created=True, resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.object == context

    def test_add_item_as_object_if_version(
        self, request_, registry, add_to, changelog, version, item):
        changelog['/'] = changelog['']._replace(created=True, resource=version)
        registry.content.get_sheet_field = Mock()
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.object == item

    def test_add_target(self, request_, add_to, changelog, context, parent):
        changelog['/'] = changelog['']._replace(created=True, resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.target == parent

    def test_add_commented_content_as_target_if_comment_created(
        self, request_, add_to, changelog, pool, service, comment):
        service['comment'] = comment
        pool['comments'] = service
        changelog['/'] = changelog['']._replace(created=True, resource=comment)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.target == pool

    def test_add_remove_activity_if_concealed(self, request_, add_to, changelog,
                                              context, parent):
        """Concealed == hidden or removed."""
        from adhocracy_core.interfaces import ActivityType
        from adhocracy_core.interfaces import VisibilityChange
        changelog['/']  = changelog['']._replace(
            visibility=VisibilityChange.concealed,
            resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.type == ActivityType.remove
        assert added_activity.target == parent

    def test_add_sheet_data_if_created(self, request_, add_to, changelog,
                                       context, mock_sheet, registry):
        registry.content.get_sheets_create.return_value = [mock_sheet]
        changelog['/'] = changelog['']._replace(created=True, resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        registry.content.get_sheets_create.assert_called_with(context,
                                                              request=request_)
        assert added_activity.sheet_data == [{mock_sheet.meta.isheet:
                                              mock_sheet.serialize()}]

    def test_add_sheet_data_if_created_version(self, request_, add_to,
            changelog, context, mock_sheet, registry, version, item):
        last_version = Mock()
        changelog['/'] = changelog['']._replace(created=True,
                                                resource=version,
                                                last_version=last_version)
        registry.content.get_sheet_field = Mock()
        self.call_fut(request_, None)
        registry.content.get_sheets_create.assert_called_with(last_version,
                                                              request=request_)

    def test_add_sheet_data_if_modified(self, request_, add_to, changelog,
                                        context, mock_sheet, registry):
        registry.content.get_sheet.return_value = mock_sheet
        appstructs = {mock_sheet.isheet: {}}
        changelog['/'] = changelog['']._replace(modified=True,
                                                modified_appstructs=appstructs,
                                                resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        registry.content.get_sheet.assert_called_with(context,
                                                      mock_sheet.isheet,
                                                      request=request_)
        assert added_activity.sheet_data == [{mock_sheet.meta.isheet:
                                              mock_sheet.serialize()}]

    def test_add_name(self, request_, add_to, changelog, context,
                      mock_generate_activity_name):
        changelog['/'] = changelog['']._replace(modified=True, resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.name == mock_generate_activity_name.return_value

    def test_add_published(self, request_, add_to, changelog, context, mocker):
        now = mocker.patch('adhocracy_core.activity.now', autospec=True)
        changelog['/'] = changelog['']._replace(modified=True, resource=context)
        self.call_fut(request_, None)
        added_activity = add_to.call_args[0][0][0]
        assert added_activity.published == now.return_value

    def test_sends_generated_event(self, request_, add_to, changelog, context,
                                   config):
        from adhocracy_core.testing import create_event_listener
        from adhocracy_core.interfaces import IActivitiesGenerated
        changelog['/'] = changelog['']._replace(modified=True, resource=context)
        added_listener = create_event_listener(config,
                                               IActivitiesGenerated)
        self.call_fut(request_, None)
        event = added_listener[0]
        added_activity = add_to.call_args[0][0][0]
        assert event.activities == [added_activity]


@fixture
def get_title(mocker):
    return mocker.patch('adhocracy_core.activity._get_title',
                        autospec=True,
                        return_value='title')


@fixture
def get_subject_name(mocker):
    return mocker.patch('adhocracy_core.activity._get_subject_name',
                        autospec=True,
                        return_value='user name')


@fixture
def get_resource_type(mocker):
    return mocker.patch('adhocracy_core.activity._get_type_name',
                        autospec=True,
                        return_value='type name')


@mark.usefixtures('get_subject_name', 'get_resource_type', 'get_title')
class TestGenerateActivityName:

    def call_fut(self, *args):
        from . import generate_activity_name
        return generate_activity_name(*args)

    def test_create_translation_with_mapping(
        self, activity, request_, get_subject_name, get_resource_type,
        get_title):
        from pyramid.i18n import TranslationString
        name = self.call_fut(activity, request_)
        get_subject_name.assert_called_with(activity.subject, request_.registry)
        get_resource_type.assert_called_with(activity.subject, request_)
        get_title.assert_called_with(activity.subject, request_.registry)
        assert isinstance(name, TranslationString)
        assert name.mapping == {'subject_name': 'user name',
                                'object_type_name': 'type name',
                                'target_title': 'title',
                                }

    def test_create_missing_translation_if_no_type(self, activity, request_):
        activity = activity._replace(type=None)
        name = self.call_fut(activity, request_)
        assert name == 'activity_missing'

    def test_create_add_translation_if_add_activity(self, activity, request_):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.add)
        name = self.call_fut(activity, request_)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_name_add'

    def test_create_add_translation_if_remove_activity(self, activity,
                                                       request_):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.remove)
        name = self.call_fut(activity, request_)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_name_remove'

    def test_create_add_translation_if_update_activity(self, activity,
                                                       request_):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.update)
        name = self.call_fut(activity, request_)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_name_update'

    def test_create_add_translation_if_transition_activity(self, activity,
                                                           request_):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.transition)
        name = self.call_fut(activity, request_)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_name_transition'


@mark.usefixtures('get_subject_name', 'get_resource_type', 'get_title')
class TestGenerateActivityDescription:

    def call_fut(self, *args):
        from . import generate_activity_description
        return generate_activity_description(*args)

    def test_create_translation_with_mapping(
        self, activity, request_, get_subject_name, get_resource_type,
        get_title):
        from pyramid.i18n import TranslationString
        name = self.call_fut(activity, request_)
        get_subject_name.assert_called_with(activity.subject, request_.registry)
        get_resource_type.assert_called_with(activity.subject, request_)
        get_title.assert_called_with(activity.subject, request_.registry)
        assert isinstance(name, TranslationString)
        assert name.mapping == {'subject_name': 'user name',
                                'object_title': 'title',
                                'object_type_name': 'type name',
                                'target_title': 'title',
                                'target_type_name': 'type name',
                                }

    def test_create_missing_translation_if_no_type(self, activity, request_):
        activity = activity._replace(type=None)
        name = self.call_fut(activity, request_)
        assert name == 'activity_missing'

    def test_create_add_translation_if_add_activity(self, activity, request_):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.add)
        name = self.call_fut(activity, request_)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_description_add'

    def test_create_add_translation_if_remove_activity(self, activity, request_):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.remove)
        name = self.call_fut(activity, request_)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_description_remove'

    def test_create_add_translation_if_update_activity(self, activity, request_):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.update)
        name = self.call_fut(activity, request_)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_description_update'

    def test_create_add_translation_if_transition_activity(self, activity,
                                                           request_):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(type=ActivityType.transition)
        name = self.call_fut(activity, request_)
        assert name.default.format_map(name.mapping)
        assert name == 'activity_description_transition'


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


def test_get_type_name_return_content_name(context, request_, registry,
                                           resource_meta):
    from . import _get_type_name
    request_.registry = registry
    registry.content.resources_meta[resource_meta.iresource] =\
        resource_meta._replace(content_name='Resource')
    assert _get_type_name(context, request_) == 'Resource'


def test_get_type_name_return_translated_content_name(context, request_,
                                                      registry, resource_meta):
    from . import _get_type_name
    request_.localizer.translate = Mock()
    request_.registry = registry
    registry.content.resources_meta[resource_meta.iresource] =\
        resource_meta._replace(content_name='Resource')
    assert _get_type_name(context,
                          request_) is request_.localizer.translate.return_value


def test_get_type_name_return_empty_if_none(request_):
    from . import _get_type_name
    assert _get_type_name(None, request_) == ''


def test_get_title_return_title(registry):
    from adhocracy_core.sheets.title import ITitle
    from . import _get_title
    context = testing.DummyResource(__provides__=ITitle)
    registry.content.get_sheet_field = Mock(return_value='title')
    assert _get_title(context, registry) == 'title'
    registry.content.get_sheet_field.assert_called_with(context, ITitle,
                                                        'title')


def test_get_title_return_title_of_last_version_if_item(registry, item):
    from unittest.mock import call
    from adhocracy_core.sheets.title import ITitle
    from adhocracy_core.sheets.tags import ITags
    from . import _get_title
    version = testing.DummyResource(__provides__=ITitle)
    registry.content.get_sheet_field = Mock(side_effect=(version, 'title'))
    assert _get_title(item, registry) == 'title'
    call_args_list = registry.content.get_sheet_field.call_args_list
    assert call_args_list[0] == call(item, ITags, 'LAST')
    assert call_args_list[1] == call(version, ITitle, 'title')


def test_get_title_return_content_of_last_version_if_comment(registry, item):
    from unittest.mock import call
    from adhocracy_core.sheets.comment import IComment
    from adhocracy_core.sheets.tags import ITags
    from . import _get_title
    version = testing.DummyResource(__provides__=IComment)
    registry.content.get_sheet_field = Mock(side_effect=(version, 'title'))
    assert _get_title(item, registry) == 'title'
    call_args_list = registry.content.get_sheet_field.call_args_list
    assert call_args_list[0] == call(item, ITags, 'LAST')
    assert call_args_list[1] == call(version, IComment, 'content')



def test_get_title_return_empty_if_missing_sheet(registry):
    from . import _get_title
    context = testing.DummyResource()
    assert _get_title(context, registry) == ''


def test_get_title_return_empty_string_if_none(registry):
    from . import _get_title
    assert _get_title(None, registry) == ''

