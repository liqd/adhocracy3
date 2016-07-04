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
        from adhocracy_core.sheets.notification import IFollowable
        return activity._replace(
            subject=testing.DummyResource(),
            type=ActivityType.add,
            object=testing.DummyResource(__provides__=IFollowable),
            target=testing.DummyResource(__provides__=IFollowable),
        )

    @fixture
    def registry(self, registry, mock_messenger):
        registry.messenger = mock_messenger
        return registry

    @fixture
    def event(self, request_, registry, context):
        from adhocracy_core.events import ActivitiesAddedToAuditLog
        request_.registry = registry
        registry.root = context
        return ActivitiesAddedToAuditLog(None, [], request_)

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
                                   mock_messenger, search_result):
        event.activities = [activity]
        mock_catalogs.search.return_value =\
            search_result._replace(elements=[])
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called

    def test_ignore_if_follower_is_subject(self, event, activity, mock_catalogs,
                                           mock_messenger, search_result):
        event.activities = [activity]
        mock_catalogs.search.return_value =\
            search_result._replace(elements=[activity.subject])
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called

    def test_ignore_if_no_followable(self, event, activity, mock_catalogs,
                                     mock_messenger, search_result):
        from zope.interface.declarations import noLongerProvides
        from adhocracy_core.sheets.notification import IFollowable
        noLongerProvides(activity.object, IFollowable)
        noLongerProvides(activity.target, IFollowable)
        event.activities = [activity]
        other_user = testing.DummyResource()
        mock_catalogs.search.return_value =\
            search_result._replace(elements=[other_user])
        self.call_fut(event)
        assert not mock_messenger.send_activity_mail.called

    def test_send_emails_to_followers(self, event, activity, mock_catalogs,
                                      mock_messenger, search_result):
        event.activities = [activity]
        other_user = testing.DummyResource()
        mock_catalogs.search.return_value =\
            search_result._replace(elements=[other_user])
        self.call_fut(event)
        mock_messenger.send_activity_mail.assert_called_with(
            other_user, activity, event.request)


@fixture
def integration(config) -> Configurator:
    config.include('adhocracy_core.notification')
    return config


@mark.usefixtures('integration')
def test_register_subscriber(registry):
    from . import subscribers
    handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
    assert subscribers.send_activity_notification_emails.__name__ in handlers

