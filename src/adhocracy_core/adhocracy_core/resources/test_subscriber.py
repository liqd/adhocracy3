from unittest.mock import Mock

from pytest import mark
from pytest import raises
from pytest import fixture
from pyramid import testing

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.testing import register_sheet


class IDummySheetAutoUpdate(ISheet, ISheetReferenceAutoUpdateMarker):
    pass


class IDummySheetNoAutoUpdate(ISheet):
    pass


def create_new_reference_event(context,
                               registry,
                               isheet=IDummySheetAutoUpdate,
                               isheet_field='elements',
                               creator=None,
                               old_version=None,
                               new_version=None,
                               root_versions=None,
                               is_batchmode=False,
                               ):
    from zope.interface import verify
    from adhocracy_core.interfaces import ISheetReferenceNewVersion
    event = testing.DummyResource(__provides__= ISheetReferenceNewVersion,
                                  object=context,
                                  isheet=isheet,
                                  isheet_field=isheet_field,
                                  old_version=old_version,
                                  new_version=new_version,
                                  registry=registry,
                                  creator=creator,
                                  root_versions=root_versions or [],
                                  is_batchmode=is_batchmode,
                                  )
    assert verify.verifyObject(ISheetReferenceNewVersion, event)
    return event


@fixture
def version():
    """Return dummy resource with IItemVersion interfaces."""
    from adhocracy_core.interfaces import IItemVersion
    version = testing.DummyResource(__provides__=IItemVersion)
    return version


@fixture
def item(version):
    from adhocracy_core.interfaces import IItem
    item = testing.DummyResource(__provides__=IItem)
    item['version'] = version
    return item


@fixture
def event(changelog, context):
    registry = testing.DummyResource()
    registry.changelog = changelog
    event = testing.DummyResource(object=context, registry=registry)
    return event


@fixture
def registry(registry_with_content, changelog):
    registry_with_content.changelog = changelog
    return registry_with_content


@fixture
def mock_download(mocker):
    mock = mocker.patch('adhocracy_core.resources.subscriber.'
                        '_download_picture_url')
    return mock


class TestAutoupdateVersionableHasNewVersion:

    @fixture
    def mock_sheet(self, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IDummySheetAutoUpdate)
        mock_sheet.get.return_value = {'elements': []}
        return mock_sheet

    def call_fut(self, event):
        from adhocracy_core.resources.subscriber import \
            autoupdate_versionable_has_new_version
        return autoupdate_versionable_has_new_version(event)

    def test_with_root_versions_not_in_subtree(self, version, mock_graph,
                                               registry):
        """Ingore event if object ist not in root_versions subtree."""
        root_version = testing.DummyResource()
        mock_graph.is_in_subtree.return_value = False
        version.__graph__ = mock_graph
        event = create_new_reference_event(version, registry,
                                           root_versions=[root_version])
        self.call_fut(event)
        mock_graph.is_in_subtree.assert_called_once_with(version, [root_version])
        assert registry.content.create.called is False

    def test_with_sheet_not_editable(self, version, registry, mock_sheet):
        """Ingore event if isheet ist not editable."""
        event = create_new_reference_event(version, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False)
        register_sheet(version, mock_sheet, registry)
        self.call_fut(event)
        assert registry.content.create.called is False

    def test_transaction_version_created_multiple_elements(
            self, version, registry, mock_sheet, changelog_meta):
        """Update version created in transaction (sheet field is list) """
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3,
                                           isheet_field='elements')
        register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        registry.changelog['/'] = changelog_meta._replace(created=True)
        self.call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}
        assert registry.content.create.called is False

    def test_transation_version_created_single_element(
            self, version, registry, mock_sheet, changelog_meta):
        """Update version created in transaction (sheet field is single)"""
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3,
                                           isheet_field='element')
        register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'element': 2}
        registry.changelog['/'] = changelog_meta._replace(created=True)
        self.call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'element': 3}
        assert registry.content.create.called is False

    def test_transaction_version_followed_by(
            self, version, registry, mock_sheet, changelog_meta):
        """Update followed_by version created in transaction."""
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        register_sheet(version, mock_sheet, registry)
        followedby = testing.DummyResource()
        register_sheet(followedby, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        registry.changelog['/'] = changelog_meta._replace(followed_by=followedby)
        self.call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}
        assert registry.content.create.called is False

    def test_transaction_version_batchmode(
            self, item, version, registry, mock_sheet, changelog_meta):
        """Update items last_version created in transaction if batchmode.

           We could create forks if we update followedby/created during batch
           request. So we just take the last created item version.
        """
        from pyramid.traversal import resource_path
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3, is_batchmode=True)
        register_sheet(version, mock_sheet, registry)
        last_version = testing.DummyResource()
        register_sheet(last_version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        registry.changelog[resource_path(item)] =\
            changelog_meta._replace(last_version=last_version)
        self.call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}
        assert registry.content.create.called is False

    @fixture
    def mock_get_last_version(self, mocker):
        from . import subscriber
        mock = mocker.patch.object(subscriber, '_get_last_version',
                                   autospec=True)
        return mock

    @fixture
    def mock_versionable_sheet(self, mock_sheet, sheet_meta):
        from copy import deepcopy
        from adhocracy_core.sheets.versions import IVersionable
        versionable = deepcopy(mock_sheet)
        versionable.get.return_value = {'follows': []}
        versionable.meta = sheet_meta._replace(isheet=IVersionable)
        return versionable

    def test_version_is_last_version(
            self, item, version, registry, mock_sheet, mock_versionable_sheet,
            mock_get_last_version):
        """If no version created in transaction and version is the items
           last_version create a new version.
        """
        from adhocracy_core.interfaces import IItemVersion
        from adhocracy_core.sheets.versions import IVersionable
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        mock_get_last_version.return_value = version
        registry.content.get_sheets_all.return_value = [mock_sheet,
                                                        mock_versionable_sheet]
        self.call_fut(event)
        assert registry.content.create.call_args[0][0] == IItemVersion.__identifier__
        assert registry.content.create.call_args[1]['root_versions'] == event.root_versions
        assert registry.content.create.call_args[1]['registry'] == event.registry
        assert registry.content.create.call_args[1]['creator'] is event.creator
        assert registry.content.create.call_args[1]['parent'] is item
        assert registry.content.create.call_args[1]['is_batchmode'] == event.is_batchmode
        assert registry.content.create.call_args[1]['appstructs'] ==\
            {IDummySheetAutoUpdate.__identifier__: {'elements': [1, 3]},
             IVersionable.__identifier__: {'follows': [version]}}

    @fixture
    def mock_sheet_readonly(self, mock_sheet, sheet_meta):
        from copy import deepcopy
        mock_readonly = deepcopy(mock_sheet)
        isheet = IDummySheetNoAutoUpdate
        mock_readonly.meta = sheet_meta._replace(isheet=isheet,
                                                 creatable=False,
                                                 editable=False)
        return mock_readonly

    def test_version_is_last_version_with_readonly_sheet(
            self, version, registry, mock_sheet,
            mock_versionable_sheet, mock_get_last_version, mock_sheet_readonly):
        """If creating a new version, do not copy readonly sheets"""
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        mock_get_last_version.return_value = version
        registry.content.get_sheets_all.return_value = [mock_sheet,
                                                        mock_versionable_sheet,
                                                        mock_sheet_readonly]
        registry.content.get_sheet.side_effect = [mock_sheet,
                                                  mock_sheet_readonly]
        self.call_fut(event)
        assert mock_sheet_readonly.meta.isheet.__identifier__ not in \
               registry.content.create.call_args[1]['appstructs']

    def test_version_is_not_last_version_but_has_same_references(
            self, version, registry, mock_sheet,
            mock_versionable_sheet, mock_get_last_version):
        """If no new version is created in transaction and version is not
           items last_version but has same references ignore
        """
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        last = testing.DummyResource()
        register_sheet(last, mock_sheet, registry)
        mock_get_last_version.return_value = last
        registry.content.get_sheets_all.return_value = [mock_sheet,
                                                        mock_versionable_sheet]
        self.call_fut(event)
        assert registry.content.create.called is False

    def test_version_is_not_last_version_and_has_not_same_references(
            self, version, registry, mock_sheet,
            mock_versionable_sheet, mock_get_last_version):
        """If no new version is created in transaction and version is not
           items last_version but has same references raise
        """
        from adhocracy_core.exceptions import AutoUpdateNoForkAllowedError
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3)
        register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        last = testing.DummyResource()
        register_sheet(last, mock_sheet, registry)
        mock_sheet.get.side_effect = [{'elements': [1, 2]}, {'elements': [11]},
                                      {'elements': [22]}]
        mock_get_last_version.return_value = last
        registry.content.get_sheets_all.return_value = [mock_sheet,
                                                        mock_versionable_sheet]
        with raises(AutoUpdateNoForkAllowedError) as err:
            self.call_fut(event)
        assert err.value.resource is version
        assert err.value.event is event


class TestAutoupdateNoneVersionableHasNewVersion:

    @fixture
    def mock_sheet(self, mock_sheet):
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IDummySheetAutoUpdate)
        mock_sheet.get.return_value = {'elements': []}
        return mock_sheet

    def call_fut(self, event):
        from adhocracy_core.resources.subscriber import \
            autoupdate_non_versionable_has_new_version
        return autoupdate_non_versionable_has_new_version(event)

    def test_with_root_versions_not_in_subtree(self, version, mock_graph,
                                               registry, mock_sheet):
        """Ingore event if object ist not in root_versions subtree."""
        root_version = testing.DummyResource()
        mock_graph.is_in_subtree.return_value = False
        version.__graph__ = mock_graph
        event = create_new_reference_event(version, registry,
                                           root_versions=[root_version])
        register_sheet(version, mock_sheet, registry)
        self.call_fut(event)
        mock_graph.is_in_subtree.assert_called_once_with(version, [root_version])
        assert not mock_sheet.set.called

    def test_with_sheet_not_editable(self, version, registry, mock_sheet):
        """Ingore event if isheet ist not editable."""
        event = create_new_reference_event(version, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False)
        register_sheet(version, mock_sheet, registry)
        self.call_fut(event)
        assert not mock_sheet.set.called

    def test_multiple_elements(self, version, registry, mock_sheet):
        """Update version (sheet field is list) """
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3,
                                           isheet_field='elements')
        register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        self.call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}

    def test_single_element(self, version, registry, mock_sheet):
        """Update version (sheet field is list) """
        event = create_new_reference_event(version, registry, old_version=2,
                                           new_version=3,
                                           isheet_field='elements')
        register_sheet(version, mock_sheet, registry)
        mock_sheet.get.return_value = {'elements': [1, 2]}
        self.call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'elements': [1, 3]}


class TestAddDefaultGroupToUserSubscriber:

    @fixture
    def principals(self, pool, service):
        from adhocracy_core.interfaces import DEFAULT_USER_GROUP_NAME
        pool['principals'] = service
        pool['principals']['groups'] = service.clone()
        group = testing.DummyResource()
        pool['principals']['groups'][DEFAULT_USER_GROUP_NAME] = group
        pool['principals']['users'] = service.clone()
        user = testing.DummyResource()
        pool['principals']['users']['000000'] = user
        return pool['principals']

    @fixture
    def event(event, registry):
        event.registry = registry
        return event

    def call_fut(self, event):
        from adhocracy_core.resources.subscriber import\
            add_default_group_to_user
        return add_default_group_to_user(event)

    def test_default_group_exists_and_no_group_set(
            self, registry, principals, event, mock_sheet, mock_user_locator):
        from adhocracy_core.interfaces import DEFAULT_USER_GROUP_NAME
        from adhocracy_core.sheets.principal import IPermissions
        default_group = principals['groups'][DEFAULT_USER_GROUP_NAME]
        user = principals['users']['000000']
        event.object = user
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        register_sheet(event.object, mock_sheet, registry)
        mock_sheet.get.return_value = {'groups': []}
        mock_user_locator.get_groups.return_value = []
        self.call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'groups': [default_group]}

    def test_default_group_exists_and_group_set(
            self, registry, principals, event, mock_sheet, mock_user_locator):
        from adhocracy_core.interfaces import DEFAULT_USER_GROUP_NAME
        from adhocracy_core.sheets.principal import IPermissions
        default_group = principals['groups'][DEFAULT_USER_GROUP_NAME]
        other_group = testing.DummyResource()
        user = principals['users']['000000']
        event.object = user
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        register_sheet(event.object, mock_sheet, registry)
        mock_sheet.get.return_value = {'groups': []}
        mock_user_locator.get_groups.return_value = [other_group]
        self.call_fut(event)
        assert mock_sheet.set.called is False

    def test_default_group_not_exists(
            self, registry, principals, event, mock_sheet):
        from adhocracy_core.interfaces import DEFAULT_USER_GROUP_NAME
        from adhocracy_core.sheets.principal import IPermissions
        del principals['groups'][DEFAULT_USER_GROUP_NAME]
        user = principals['users']['000000']
        event.object = user
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        register_sheet(event.object, mock_sheet, registry)
        mock_sheet.get.return_value = {'groups': []}
        self.call_fut(event)
        assert mock_sheet.set.called is False


class TestUpdateModificationDate:

    def call_fut(self, event):
        from .subscriber import update_modification_date_modified_by
        return update_modification_date_modified_by(event)

    def test_with_request(self, context, registry, mock_sheet, monkeypatch):
        from datetime import datetime
        from . import subscriber
        from adhocracy_core.sheets.metadata import IMetadata
        now = datetime.now()
        monkeypatch.setattr(subscriber, 'get_modification_date', lambda x: now)
        register_sheet(context, mock_sheet, registry, isheet=IMetadata)
        request = testing.DummyResource(user=object())
        event = testing.DummyResource(object=context,
                                      registry=registry,
                                      request=request)
        self.call_fut(event)
        assert mock_sheet.set.call_args[0][0] == {'modification_date': now,
                                                  'modified_by': request.user}
        assert mock_sheet.set.call_args[1] == {'send_event': False,
                                               'omit_readonly': False}


class TestSendPasswordResetMail:

    @fixture
    def registry(self, registry, mock_messenger):
        registry.messenger = mock_messenger
        return registry

    @fixture
    def event(self, context, registry):
        event.object = context
        event.registry = registry
        return event

    def call_fut(self, event):
        from .subscriber import send_password_reset_mail
        return send_password_reset_mail(event)

    def test_call(self, event, mock_sheet, registry, mock_messenger):
        user = testing.DummyResource()
        mock_sheet.get.return_value = {'creator': user}
        registry.content.get_sheet.return_value = mock_sheet
        event.object.__name__ = '/reset'
        self.call_fut(event)
        mock_messenger.send_password_reset_mail.assert_called_with(user,
                                                                   event.object)


class TestSendPasswordChangeMail:

    @fixture
    def registry(self, registry, mock_messenger):
        registry.messenger = mock_messenger
        return registry

    @fixture
    def event(self, context, registry):
        event.object = context
        event.registry = registry
        return event

    def call_fut(self, event):
        from .subscriber import send_password_change_mail
        return send_password_change_mail(event)

    def test_call(self, event, mock_sheet, registry, mock_messenger):
        user = testing.DummyResource()
        mock_sheet.get.return_value = {'creator': user}
        registry.content.get_sheet.return_value = mock_sheet
        self.call_fut(event)
        mock_messenger.send_password_change_mail.assert_called_with(user)


class TestApplyUserActivationConfiguration:

    @fixture
    def registry(self, registry, mock_messenger):
        registry.messenger = mock_messenger
        return registry

    @fixture
    def user(self):
        user = testing.DummyResource(name='user name',
                                     email='test@test.de',
                                     activate=Mock())
        return user

    @fixture
    def event(self, user, registry):
        event.object = user
        event.registry = registry
        return event

    @fixture
    def mock_sheet(self, registry, mock_sheet):
        registry.content.get_sheet.return_value = mock_sheet
        return mock_sheet

    def call_fut(self, event):
        from .subscriber import apply_user_activation_configuration
        return apply_user_activation_configuration(event)

    def test_activate_directly(self, event, mock_messenger, mock_sheet):
        mock_sheet.get.return_value = {'activation': 'direct'}
        self.call_fut(event)
        assert event.object.activate.called
        assert mock_messenger.send_registration_mail.called is False
        assert mock_messenger.send_invitation_mail.called is False

    def test_send_registration_mail(self, event, mock_messenger, mock_sheet):
        mock_sheet.get.return_value = {'activation': 'registration_mail'}
        self.call_fut(event)
        send_mail_call_args = mock_messenger.send_registration_mail.call_args[0]
        assert send_mail_call_args[0] == event.object
        assert send_mail_call_args[1].startswith('/activate/')
        assert event.object.activation_path.startswith('/activate/')
        assert event.object.activate.called is False
        assert mock_messenger.send_invitation_mail.called is False

    def test_registration_if_messenger_is_none(self, registry, event,
                                               mock_messenger, mock_sheet):
        mock_sheet.get.return_value = {'activation': 'registration_mail'}
        registry.messenger = None
        self.call_fut(event)
        assert mock_messenger.send_registration_mail.called is False
        assert mock_messenger.send_invitation_mail.called is False

    def test_send_invitation_mail(self, event, mock_messenger, mock_sheet,
                                  registry):
        mock_sheet.get.return_value = {'activation': 'invitation_mail'}
        reset_mock = Mock()
        registry.content.create.return_value = reset_mock
        self.call_fut(event)
        send_mail_call_args = mock_messenger.send_invitation_mail.call_args[0]
        assert send_mail_call_args[0] == event.object
        assert send_mail_call_args[1] == reset_mock
        assert event.object.activate.called is False
        assert mock_messenger.send_registration_mail.called is False

    def test_invitation_if_messenger_is_none(self, registry, event,
                                             mock_messenger, mock_sheet):
        mock_sheet.get.return_value = {'activation': 'invitation_mail'}
        registry.messenger = None
        self.call_fut(event)
        assert mock_messenger.send_registration_mail.called is False
        assert mock_messenger.send_invitation_mail.called is False


class TestUpdateDownload:

    def call_fut(self, event):
        from .subscriber import update_asset_download
        return update_asset_download(event)

    def test_call(self, mocker, event, context, registry):
        from . import subscriber
        mock = mocker.patch.object(subscriber, 'add_metadata', autspec=True)
        self.call_fut(event)
        mock.assert_called_with(event.object, event.registry)


class TestUpdateImageDownload:

    def call_fut(self, event):
        from .subscriber import update_image_downloads
        return update_image_downloads(event)

    def test_call(self, mocker, event, context, registry):
        from . import subscriber
        mock = mocker.patch.object(subscriber, 'add_image_size_downloads')
        self.call_fut(event)
        assert mock.called_with(event.object, event.registry)


class TestDownloadPictureForVersion:

    @fixture
    def event(self, event, version, registry):
        event.registry = registry
        event.new_version = version
        return event

    def call_fut(self, *args):
        from .subscriber import download_external_picture_for_version
        return download_external_picture_for_version(*args)


    def test_call_download_picture_url(self, event, mock_download, registry,
                                       mock_sheet):
        from copy import deepcopy
        old_sheet = mock_sheet
        old_sheet.get.return_value = {'external_picture_url': 'old_url'}
        new_sheet = deepcopy(mock_sheet)
        new_sheet.get.return_value = {'external_picture_url': 'new_url'}
        registry.content.get_sheet.side_effect = (old_sheet, new_sheet)
        self.call_fut(event)
        mock_download.assert_called_with(event.new_version, 'old_url',
                                         'new_url', registry)


class TestDownloadPictureForCreated:

    @fixture
    def event(self, event, registry):
        event.registry = registry
        return event

    def call_fut(self, *args):
        from .subscriber import download_external_picture_for_created
        return download_external_picture_for_created(*args)

    def test_ignore_if_context_is_versionable(self, event, version,
                                              mock_download):
        event.object = version
        self.call_fut(event)
        assert not mock_download.called

    def test_call_download_picture_url(self, event, mock_download, registry,
                                       mock_sheet):
        mock_sheet.get.return_value = {'external_picture_url': 'new_url'}
        registry.content.get_sheet.return_value = mock_sheet
        self.call_fut(event)
        mock_download.assert_called_with(event.object, '',
                                         'new_url', registry)


class TestDownloadPictureForEdited:

    @fixture
    def event(self, event, registry):
        event.registry = registry
        return event

    def call_fut(self, *args):
        from .subscriber import download_external_picture_for_edited
        return download_external_picture_for_edited(*args)

    def test_call_download_picture_url(self, event, mock_download, registry):
        event.old_appstruct = {'external_picture_url': 'old_url'}
        event.new_appstruct = {'external_picture_url': 'new_url'}
        self.call_fut(event)
        mock_download.assert_called_with(event.object, 'old_url',
                                         'new_url', registry)

    def test_call_download_picture_url_with_empty_string_if_not_set(
            self, event, mock_download, registry):
        event.old_appstruct = {}
        event.new_appstruct = {}
        self.call_fut(event)
        mock_download.assert_called_with(event.object, '',
                                         '', registry)



class TestDownloadExternalPictureUrl:

    def call_fut(self, *args):
        from .subscriber import _download_picture_url
        return _download_picture_url(*args)

    def test_ignore_if_picture_url_not_changed(self, context, registry):
        old_url = 'http://x'
        new_url = 'http://x'
        self.call_fut(context, old_url, new_url, registry)
        assert not registry.content.create.called

    def test_remove_picture_reference_if_picture_url_changed_to_empty(
            self, context, registry, mock_sheet):
        registry.content.get_sheet.return_value = mock_sheet
        old_url = 'http://x'
        new_url = ''
        self.call_fut(context, old_url, new_url, registry)
        mock_sheet.set.assert_called_with({'picture': None}, send_event=False)

    def test_download_picture_url_and_reference_if_picture_url_changed(
            self, context, registry, mock_sheet, mocker):
        from adhocracy_core.sheets.asset import IAssetData
        from .image import IImage
        image = Mock()
        file = mocker.patch('adhocracy_core.resources.subscriber.'
                            'File').return_value
        assets = mocker.patch('adhocracy_core.resources.subscriber.'
                              'find_service').return_value
        registry.content.create.return_value = image
        registry.content.get_sheet.return_value = mock_sheet
        resp = Mock(content=b'sdfsdf', headers={'Content-Length': 11})
        mocker.patch('requests.get', return_value=resp)

        old_url = ''
        new_url = 'http://x'
        self.call_fut(context, old_url, new_url, registry)

        assert file.size == 11
        registry.content.create.assert_called_with(
            IImage.__identifier__,
            parent=assets,
            registry=registry,
            appstructs={IAssetData.__identifier__: {'data': file}})
        mock_sheet.set.assert_called_with({'picture': image}, send_event=False)


class TestAddActivitiesToActivityStream:

    @fixture
    def event(self, event, registry, request_):
        event.registry = registry
        event.request = request_
        return event

    @fixture
    def activity(self, activity):
        from adhocracy_core.interfaces import ActivityType
        from adhocracy_core.utils import now
        return activity._replace(
            subject=testing.DummyResource(),
            type=ActivityType.add,
            object=testing.DummyResource(),
            target=testing.DummyResource(),
            published=now()
        )

    @fixture
    def mock_activity_stream(self, mocker):
        activity_stream = testing.DummyResource()
        mocker.patch('adhocracy_core.resources.subscriber.find_service',
                     return_value=activity_stream)
        return activity_stream

    def call_fut(self, *args):
        from .subscriber import add_activities_to_activity_stream
        return add_activities_to_activity_stream(*args)

    def test_ignore_if_no_activities(self, event, registry):
        event.activities = []
        self.call_fut(event)
        assert not registry.content.create.called


    def test_ignore_per_default(self, event, registry, activity):
        event.activities = [activity]
        self.call_fut(event)
        assert not registry.content.create.called

    def test_ignore_if_disabled(self, event, registry, activity):
        registry.settings['adhocracy.activity_stream.enabled'] = "False"
        event.activities = [activity]
        self.call_fut(event)
        assert not registry.content.create.called

    def test_create_activities_if_enabled(self, event, registry, activity,
                                          mock_activity_stream, mocker):
        from adhocracy_core.resources.activity import IActivity
        import adhocracy_core.sheets.activity
        registry.settings['adhocracy.activity_stream.enabled'] = "True"
        event.activities = [activity]
        mocker.patch('adhocracy_core.resources.subscriber' +
                     '.generate_activity_description',
                     return_value='description')
        self.call_fut(event)
        expected_appstructs = {
            adhocracy_core.sheets.activity.IActivity.__identifier__: {
                'subject': activity.subject,
                'type': activity.type.value,
                'object': activity.object,
                'target': activity.target,
                'name': 'description',
                'published': activity.published,
            }
        }
        registry.content.create.assert_called_with(
            IActivity.__identifier__,
            registry=registry,
            parent=mock_activity_stream,
            appstructs=expected_appstructs)


@mark.usefixtures('integration')
def test_register_subscriber(registry):
    from adhocracy_core.resources import subscriber
    from adhocracy_core.authorization import set_acms_for_app_root
    handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
    assert subscriber.autoupdate_non_versionable_has_new_version.__name__ in handlers
    assert subscriber.autoupdate_versionable_has_new_version.__name__ in handlers
    assert subscriber.add_default_group_to_user.__name__ in handlers
    assert subscriber.update_modification_date_modified_by.__name__ in handlers
    assert subscriber.send_password_reset_mail.__name__ in handlers
    assert subscriber.apply_user_activation_configuration.__name__ in handlers
    assert subscriber.update_asset_download.__name__ in handlers
    assert subscriber.update_image_downloads.__name__ in handlers
    assert set_acms_for_app_root.__name__ in handlers
    assert subscriber.download_external_picture_for_created.__name__ in handlers
    assert subscriber.download_external_picture_for_version.__name__ in handlers
    assert subscriber.download_external_picture_for_edited.__name__ in handlers


