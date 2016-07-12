from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises
from unittest.mock import Mock


@fixture
def registry(registry_with_content):
    return registry_with_content


class TestNotificationSheet:

    @fixture
    def meta(self):
        from .notification import notification_meta
        return notification_meta

    def test_meta(self, meta):
        from . import notification
        assert meta.isheet == notification.INotification
        assert meta.schema_class == notification.NotificationSchema
        assert meta.editable is True
        assert meta.creatable is True
        assert meta.readable is True
        assert meta.permission_edit == 'edit_notification'

    def test_create(self, meta, context):
        from .notification import get_follow_choices
        inst = meta.sheet_class(meta, context, None)
        assert inst
        assert inst.schema['follow_resources'].choices_getter ==\
               get_follow_choices

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'follow_resources': []}

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, config):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert config.registry.content.get_sheet(context, meta.isheet)


class TestGetFollowChoicesGetter:

    def call_fut(self, *args):
        from .notification import get_follow_choices
        return get_follow_choices(*args)

    def test_create_followable_choices(self, request_, mocker, mock_catalogs,
                                       search_result):
        from .notification import IFollowable
        context = testing.DummyResource(__name__='followable')
        mocker.patch('adhocracy_core.sheets.notification.find_service',
                     return_value=mock_catalogs)
        mock_catalogs.search.return_value = search_result._replace(elements=
                                                                   [context])
        result = self.call_fut(context, request_)
        assert mock_catalogs.search.call_args[0][0].interfaces == IFollowable
        assert result == [('http://example.comfollowable/', 'followable')]


class TestFollowableSheet:

    @fixture
    def meta(self):
        from .notification import followable_meta
        return followable_meta

    def test_meta(self, meta):
        from . import notification
        assert meta.isheet == notification.IFollowable
        assert meta.editable is False
        assert meta.creatable is False
        assert meta.readable is True

    def test_create(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {}

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, config):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert config.registry.content.get_sheet(context, meta.isheet)
