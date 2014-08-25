from copy import deepcopy

from pyramid import testing
from pytest import fixture

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.sheets.versions import IVersionable
from zope.interface import directlyProvides


class IDummySheetAutoUpdate(ISheet, ISheetReferenceAutoUpdateMarker):
    pass


class IDummySheetNoAutoUpdate(ISheet):
    pass


def add_and_register_sheet(context, mock_sheet, registry):
    from zope.interface import alsoProvides
    from adhocracy.interfaces import IResourceSheet
    isheet = mock_sheet.meta.isheet
    alsoProvides(context, isheet)
    registry.registerAdapter(lambda x: mock_sheet, (isheet,),
                             IResourceSheet,
                             isheet.__identifier__)


def _create_new_version_event_with_isheet(context, isheet, registry, creator=None):
    return testing.DummyResource(__provides__=
                                 ISheetReferencedItemHasNewVersion,
                                 object=context,
                                 isheet=isheet,
                                 isheet_field='elements',
                                 old_version=testing.DummyResource(),
                                 new_version=testing.DummyResource(),
                                 registry=registry,
                                 creator=creator,
                                 root_versions=[])


class TestReferenceHasNewVersionSubscriberUnitTest:

    @fixture
    def registry(self, config, registry, mock_resource_registry, transaction_changelog):
        registry.content = mock_resource_registry
        registry._transaction_changelog = transaction_changelog
        return registry

    def _make_one(self, *args):
        from adhocracy.subscriber import reference_has_new_version_subscriber
        return reference_has_new_version_subscriber(*args)

    def _create_new_version_event_for_autoupdate_sheet(self, context, registry, mock_sheet):
        event = _create_new_version_event_with_isheet(context, IDummySheetAutoUpdate, registry)
        sheet_autoupdate = deepcopy(mock_sheet)
        sheet_autoupdate.meta = mock_sheet.meta._replace(isheet=IDummySheetAutoUpdate)
        sheet_autoupdate.get.return_value = {'elements': [event.old_version]}
        add_and_register_sheet(context, sheet_autoupdate, registry)
        sheet_versionable = deepcopy(mock_sheet)
        sheet_versionable.meta = mock_sheet.meta._replace(isheet=IVersionable)
        sheet_versionable.get.return_value = {'follows': []}
        add_and_register_sheet(context, sheet_versionable, registry)
        return event

    def test_call_versionable_with_autoupdate_sheet_once(self, context, registry, mock_sheet):
        directlyProvides(context, IItemVersion)
        event = self._create_new_version_event_for_autoupdate_sheet(context, registry, mock_sheet)
        event.creator = object()

        self._make_one(event)

        factory = registry.content.create
        assert factory.call_count == 1
        parent = factory.call_args[1]['parent']
        assert parent is context.__parent__
        appstructs = factory.call_args[1]['appstructs']
        assert appstructs[event.isheet.__identifier__] == \
               {'elements': [event.new_version]}
        assert appstructs[IVersionable.__identifier__] == {'follows': [context]}
        creator = factory.call_args[1]['creator']
        assert creator == event.creator

    def test_call_versionable_with_autoupdate_sheet_twice(self, context, registry, mock_sheet, transaction_changelog):
        directlyProvides(context, IItemVersion)
        event = self._create_new_version_event_for_autoupdate_sheet(context, registry, mock_sheet)
        self._make_one(event)

        event_second = self._create_new_version_event_for_autoupdate_sheet(context, registry, mock_sheet)
        transaction_changelog['/'] = transaction_changelog['/']._replace(
            followed_by=event_second.new_version)
        registry._transaction_changelog = transaction_changelog
        self._make_one(event_second)

        factory = registry.content.create
        assert factory.call_count == 1

    def test_call_versionable_with_autoupdate_sheet_and_root_versions_and_not_is_insubtree(self,
            context, mock_graph, registry, mock_sheet):
        mock_graph.is_in_subtree.return_value = False
        context = testing.DummyResource(__provides__=IItemVersion,
                                        __parent__=testing.DummyResource(),
                                        __graph__=mock_graph)
        event = self._create_new_version_event_for_autoupdate_sheet(context, registry, mock_sheet)
        event.root_versions = [context]

        self._make_one(event)

        assert not registry.content.create.called

    def test_call_versionable_with_autoupdate_sheet_but_readonly(self, context, registry, mock_sheet):
        directlyProvides(context, IItemVersion)
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False,
                                                   creatable=False,
                                                   isheet=isheet)
        add_and_register_sheet(context, mock_sheet, registry)

        self._make_one(event)

        assert not registry.content.create.called

    def test_call_versionable_with_autoupdate_sheet_and_other_sheet_readonly(self, context, registry, mock_sheet):
        directlyProvides(context, IItemVersion)
        event = self._create_new_version_event_for_autoupdate_sheet(context, registry, mock_sheet)
        isheet_readonly = IDummySheetNoAutoUpdate
        mock_sheet.meta = mock_sheet.meta._replace(editable=False,
                                                   creatable=False,
                                                   isheet=isheet_readonly)
        add_and_register_sheet(context, mock_sheet, registry)

        self._make_one(event)

        assert registry.content.create.called
        assert isheet_readonly.__identifier__ not in registry.content.create.call_args[1]['appstructs']

    def test_call_versionable_without_autoupdate_sheet(self, context, registry, mock_sheet):
        directlyProvides(context, IItemVersion)
        isheet = IDummySheetNoAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False,
                                                   creatable=False,
                                                   isheet=isheet)
        add_and_register_sheet(context, mock_sheet, registry)

        self._make_one(event)

        assert not registry.content.create.called

    def test_call_nonversionable_with_autoupdate_sheet(self, context, registry, mock_sheet):
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet, registry)
        mock_sheet.meta = mock_sheet.meta._replace(isheet=isheet)
        mock_sheet.get.return_value = {'elements': [event.old_version]}
        add_and_register_sheet(context, mock_sheet, registry)

        self._make_one(event)

        assert mock_sheet.set.call_args[0][0] == {'elements': [event.new_version]}

    def test_call_nonversionable_with_autoupdate_readonly(self, context, registry, mock_sheet):
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet, registry)
        mock_sheet.meta = mock_sheet.meta._replace(editable=False,
                                                   creatable=False,
                                                   isheet=isheet)
        mock_sheet.get.return_value = {'elements': [event.old_version]}
        add_and_register_sheet(context, mock_sheet, registry)

        self._make_one(event)

        assert mock_sheet.set.called is False


def includeme_register_has_new_version_subscriber(config):
    from adhocracy.subscriber import reference_has_new_version_subscriber
    config.include('adhocracy.events')
    config.include('adhocracy.subscriber')
    handlers = config.registry.registeredHandlers()
    handler_names = [x.handler.__name__ for x in handlers]
    assert reference_has_new_version_subscriber.__name__ in handler_names
