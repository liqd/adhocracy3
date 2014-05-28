from unittest.mock import patch
import unittest

from pyramid import testing

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.sheets.versions import IVersionable


#############
#  helpers  #
#############

class IDummySheetAutoUpdate(ISheet, ISheetReferenceAutoUpdateMarker):
    pass


class IDummySheetNoAutoUpdate(ISheet):
    pass


class DummySheet:

    _data = {}

    def __init__(self, metadata, context):
        self.meta = metadata
        self.context = context

    def set(self, appstruct):
        self._data.update(appstruct)

    def get(self):
        return self._data


def _create_and_register_dummy_sheet(context, isheet):
    from pyramid.threadlocal import get_current_registry
    from zope.interface import alsoProvides
    from adhocracy.interfaces import IResourceSheet
    from adhocracy.interfaces import sheet_metadata
    registry = get_current_registry(context)
    metadata = sheet_metadata._replace(isheet=isheet)
    alsoProvides(context, isheet)
    sheet = DummySheet(metadata, context)
    registry.registerAdapter(lambda x: sheet, (isheet,),
                             IResourceSheet,
                             isheet.__identifier__)
    return sheet


def _create_new_version_event_with_isheet(context, isheet):
    return testing.DummyResource(__provides__=
                                 ISheetReferencedItemHasNewVersion,
                                 object=context,
                                 isheet=isheet,
                                 isheet_field='elements',
                                 old_version=testing.DummyResource(),
                                 new_version=testing.DummyResource(),
                                 root_versions=[])


###########
#  tests  #
###########

class ReferenceHasNewVersionSubscriberUnitTest(unittest.TestCase):

    @patch('adhocracy.registry.ResourceContentRegistry')
    def setUp(self, dummy_resource_registry=None):
        self.config = testing.setUp()
        resource_registry = dummy_resource_registry.return_value
        self.config.registry.content = resource_registry

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, *args):
        from adhocracy.subscriber import reference_has_new_version_subscriber
        return reference_has_new_version_subscriber(*args)

    def test_call_versionable_with_autoupdate_sheet(self):
        context = testing.DummyResource(__provides__=IItemVersion,
                                        __parent__=object())
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet)
        sheet_autoupdate = _create_and_register_dummy_sheet(context, isheet)
        sheet_autoupdate._data = {'elements': [event.old_version]}
        sheet_versionable = _create_and_register_dummy_sheet(event.object,
                                                             IVersionable)
        sheet_versionable._data = {'follows': []}

        self._makeOne(event)

        factory = self.config.registry.content.create
        assert factory.called
        parent = factory.call_args[1]['parent']
        assert parent is context.__parent__
        appstructs = factory.call_args[1]['appstructs']
        assert appstructs[isheet.__identifier__] == \
               {'elements': [event.new_version]}
        assert appstructs[IVersionable.__identifier__] == {'follows': [context]}

    @patch('adhocracy.graph.Graph')
    def test_call_versionable_with_autoupdate_sheet_and_root_versions_and_not_is_insubtree(self,
                                                                                           dummy_graph):
        graph = dummy_graph.return_value
        graph.is_in_subtree.return_value = False
        context = testing.DummyResource(__provides__=IItemVersion,
                                        __parent__=object(),
                                        __graph__=graph)
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet)
        event.root_versions = [context]
        sheet_autoupdate = _create_and_register_dummy_sheet(context, isheet)
        sheet_autoupdate._data = {'elements': [event.old_version]}
        sheet_versionable = _create_and_register_dummy_sheet(event.object,
                                                             IVersionable)
        sheet_versionable._data = {'follows': []}

        self._makeOne(event)

        factory = self.config.registry.content.create
        assert not factory.called

    def test_call_versionable_with_autoupdate_sheet_but_readonly(self):
        context = testing.DummyResource(__provides__=IItemVersion)
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet)
        sheet_autoupdate = _create_and_register_dummy_sheet(context, isheet)
        sheet_autoupdate.meta = sheet_autoupdate.meta._replace(
            editable=False,
            creatable=False)

        self._makeOne(event)

        factory = self.config.registry.content.create
        assert not factory.called

    def test_call_versionable_without_autoupdate_sheet(self):
        context = testing.DummyResource(__provides__=IItemVersion)
        isheet = IDummySheetNoAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet)
        _create_and_register_dummy_sheet(context, isheet)

        self._makeOne(event)

        factory = self.config.registry.content.create
        assert not factory.called

    def test_call_nonversionable_with_autoupdate_sheet(self):
        context = testing.DummyResource()
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet)
        sheet_autoupdate = _create_and_register_dummy_sheet(context, isheet)
        sheet_autoupdate._data = {'elements': [event.old_version]}

        self._makeOne(event)

        assert sheet_autoupdate._data == {'elements': [event.new_version]}

    def test_call_nonversionable_with_autoupdate_readonly(self):
        context = testing.DummyResource()
        isheet = IDummySheetAutoUpdate
        event = _create_new_version_event_with_isheet(context, isheet)
        sheet_autoupdate = _create_and_register_dummy_sheet(context, isheet)
        sheet_autoupdate.meta = sheet_autoupdate.meta._replace(editable=False,
                                                               creatable=False)
        sheet_autoupdate._data = {'elements': [event.old_version]}

        self._makeOne(event)

        assert sheet_autoupdate._data == {'elements': [event.old_version]}


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.events')
        self.config.include('adhocracy.subscriber')

    def tearDown(self):
        testing.tearDown()

    def test_register_versions_adapter(self):
        from adhocracy.subscriber import reference_has_new_version_subscriber
        handlers = [x.handler.__name__ for x
                    in self.config.registry.registeredHandlers()]
        assert len(handlers) >= 1
        assert reference_has_new_version_subscriber.__name__ in handlers
