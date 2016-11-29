from pyramid import testing
from pytest import fixture
from pytest import mark
from pyramid.config import Configurator


class TestSendActivityNotificationEmails:

    def call_fut(self, *args):
        from .subscribers import send_activity_notification_emails
        return send_activity_notification_emails(*args)

    @fixture
    def activity(self, activity):
        from adhocracy_core.interfaces import ActivityType
        return activity._replace(
            subject=testing.DummyResource(),
            type=ActivityType.add,
        )

    @fixture
    def followable(self):
        from adhocracy_core.sheets.notification import IFollowable
        return testing.DummyResource(__provides__=IFollowable)

    @fixture
    def registry(self, registry, mock_messenger):
        registry.messenger = mock_messenger
        return registry

    @fixture
    def event(self, request_, registry, context):
        from adhocracy_core.events import ActivitiesGenerated
        request_.registry = registry
        registry.root = context
        return ActivitiesGenerated([], request_)

    @fixture
    def mock_catalogs(self, mock_catalogs, mocker):
        mocker.patch('adhocracy_core.notification.subscribers.find_service',
                     return_value=mock_catalogs)
        return mock_catalogs

    def test_ignore_if_no_activities(self, event, mock_messenger):
        event.activities = []
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called

    def test_ignore_if_no_follower(self, event, activity, mock_catalogs,
                                   mock_messenger, search_result, followable):
        activity = activity._replace(target=followable)
        event.activities = [activity]
        mock_catalogs.search.return_value = search_result._replace(elements=[])
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called

    def test_ignore_if_follower_is_subject(self, event, activity, mock_catalogs,
                                           mock_messenger, search_result, followable):
        activity = activity._replace(target=followable)
        event.activities = [activity]
        mock_catalogs.search.return_value = search_result._replace(
            elements=[activity.subject])
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called

    def test_ignore_if_no_followable(self, event, activity, mock_catalogs,
                                     mock_messenger, search_result, context):
        activity = activity._replace(target=context)
        event.activities = [activity]
        other_user = testing.DummyResource()
        mock_catalogs.search.return_value = search_result._replace(
            elements=[other_user])
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called

    def test_send_activity_to_target_followers(self, event, activity,
                                               mock_catalogs, followable,
                                               mock_messenger, search_result):
        activity = activity._replace(target=followable)
        event.activities = [activity]
        user = testing.DummyResource()
        mock_catalogs.search.return_value = search_result._replace(
            elements=[user])
        self.call_fut(event)
        mock_messenger.send_activity_mail.assert_called_with(
            user, activity, event.request)

    def test_send_activity_to_object_followers(self, event, activity,
                                             mock_catalogs, followable,
                                             mock_messenger, search_result):
        from adhocracy_core.sheets.description import IDescription
        sheet_data = [{IDescription: {}}]
        activity = activity._replace(object=followable,
                                     sheet_data=sheet_data)
        event.activities = [activity]
        user = testing.DummyResource()
        mock_catalogs.search.return_value = search_result._replace(
            elements=[user])
        self.call_fut(event)
        mock_messenger.send_activity_mail.assert_called_with(
            user, activity, event.request)

    def test_send_activity_with_object_comments_to_process_followers(
        self, event, activity, mock_catalogs, mock_messenger, search_result):
        from adhocracy_core.sheets.notification import IFollowable
        from adhocracy_core.resources.comment import IComment
        from adhocracy_core.resources.process import IProcess
        process = testing.DummyResource(__provides__=(IProcess, IFollowable))
        process['some_child'] = testing.DummyResource()
        comment = testing.DummyResource(__provides__=IComment)
        process['some_child']['comment'] = comment

        activity = activity._replace(object=comment)
        event.activities = [activity]
        user = testing.DummyResource()
        mock_catalogs.search.return_value = search_result._replace(
            elements=[user])
        self.call_fut(event)
        mock_messenger.send_activity_mail.assert_called_with(
            user, activity, event.request)

    def test_ignore_if_activity_with_object_comment_but_no_process(
        self, event, activity, mock_catalogs, mock_messenger, search_result):
        from adhocracy_core.resources.comment import IComment
        comment = testing.DummyResource(__provides__=IComment)

        activity = activity._replace(object=comment)
        event.activities = [activity]
        user = testing.DummyResource()
        mock_catalogs.search.return_value = search_result._replace(
            elements=[user])
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called

    def test_ignore_if_transition(self, event, activity, mock_catalogs,
                                  mock_messenger, search_result, followable):
        from adhocracy_core.interfaces import ActivityType
        activity = activity._replace(object=followable,
                                     type=ActivityType.transition)
        event.activities = [activity]
        user = testing.DummyResource()
        mock_catalogs.search.return_value = search_result._replace(
            elements=[user])
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called

    def test_ignore_if_workflow_assignment_update(
            self, event, activity, mock_catalogs, mock_messenger,
            search_result, followable):
        from adhocracy_core.interfaces import ActivityType
        from adhocracy_core.sheets.workflow import IWorkflowAssignment
        sheet_data = [{IWorkflowAssignment: {}}]
        activity = activity._replace(object=followable,
                                     type=ActivityType.update,
                                     sheet_data=sheet_data)
        event.activities = [activity]
        user = testing.DummyResource()
        mock_catalogs.search.return_value = search_result._replace(
            elements=[user])
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called


@fixture
def integration(config) -> Configurator:
    config.include('adhocracy_core.notification')
    return config


@mark.usefixtures('integration')
def test_register_subscriber(registry):
    from . import subscribers
    handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
    assert subscribers.send_activity_notification_emails.__name__ in handlers

