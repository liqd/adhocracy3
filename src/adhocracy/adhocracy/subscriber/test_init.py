from adhocracy.interfaces import ISheet
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.utils import get_all_taggedvalues
from pyramid import testing
from unittest.mock import patch

import unittest


#############
#  helpers  #
#############

class IDummySheetAutoUpdate(ISheet, ISheetReferenceAutoUpdateMarker):
    pass


class IDummySheetNoAutoUpdate(ISheet):
    pass


class DummyPropertySheetAdapter(object):

    readonly = False

    def __init__(self, context, iface):
        self.context = context
        self.iface = iface
        self.key = self.iface.__identifier__
        self.metadata = get_all_taggedvalues(iface)
        self.readonly = self.metadata['readonly']
        if not hasattr(self.context, 'dummy_appstruct'):
            self.context.dummy_appstruct = {}
        if self.key not in self.context.dummy_appstruct:
            self.context.dummy_appstruct[self.key] = {}

    def set(self, appstruct):
        self.context.dummy_appstruct[self.key].update(appstruct)

    def get(self):
        return self.context.dummy_appstruct[self.key]


def _register_dummypropertysheet_adapter(config):
    from adhocracy.interfaces import IResourcePropertySheet
    from adhocracy.interfaces import ISheet
    from zope.interface.interfaces import IInterface
    config.registry.registerAdapter(DummyPropertySheetAdapter,
                                    (ISheet, IInterface),
                                    IResourcePropertySheet)


class DummyObjectMap():
    """Dummy object map that just returns a single resource."""

    def __init__(self, resource):
        self.resource = resource

    def object_for(self, oid):
        return self.resource

    def get_reftypes(self):
        return []


###########
#  tests  #
###########

class ReferenceHasNewVersionSubscriberUnitTest(unittest.TestCase):

    @patch('adhocracy.registry.ResourceContentRegistry', autospec=True)
    def setUp(self, dummy_content_registry=None):
        from adhocracy.interfaces import IResource
        from adhocracy.sheets.versions import IVersionable
        from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
        self.config = testing.setUp()
        # create dummy parent (Item for versionables)
        self.parent = testing.DummyResource()
        # create dummy child with sheet data (ItemVersion for versionables)
        child = testing.DummyResource(__parent__=self.parent,
                                      __oid__=0,
                                      __provides__=(IResource, IVersionable,
                                                    IDummySheetAutoUpdate,
                                                    IDummySheetNoAutoUpdate)
                                      )
        _register_dummypropertysheet_adapter(self.config)
        child.dummy_appstruct = dict([
            (IDummySheetNoAutoUpdate.__identifier__,
             {'title': u't', 'elements': [9, 1, 10]}),
            (IDummySheetAutoUpdate.__identifier__,
             {'title': u't', 'elements': [9, 1, 10]}),
            (IVersionable.__identifier__,
             {'follows': [-1]}),
        ])
        IDummySheetAutoUpdate.setTaggedValue('readonly', False)
        self.child = child
        objectmap = DummyObjectMap(child)
        child.__objectmap__ = objectmap
        # create dummy event
        self.event = testing.DummyResource(__provides__=
                                           ISheetReferencedItemHasNewVersion,
                                           object=child,
                                           isheet=IDummySheetNoAutoUpdate,
                                           isheet_field='elements',
                                           old_version_oid=1,
                                           new_version_oid=2,
                                           root_versions=[child])
        # create dummy content registry
        content_registry = dummy_content_registry.return_value
        self.config.registry.content = content_registry

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, *args):
        from . import reference_has_new_version_subscriber
        return reference_has_new_version_subscriber(*args)

    def test_call_versionable_with_autoupdate(self):
        factory = self.config.registry.content.create
        from adhocracy.sheets.versions import IVersionable
        self.event.isheet = IDummySheetAutoUpdate

        self._makeOne(self.event)
        assert factory.called
        child_new_parent = factory.call_args[1]['parent']
        child_new_appstructs = factory.call_args[1]['appstructs']
        assert child_new_parent is self.child.__parent__
        child_new_wanted_appstructs = dict([
            (IDummySheetNoAutoUpdate.__identifier__,
             {'title': u't', 'elements': [9, 1, 10]}),
            (IDummySheetAutoUpdate.__identifier__,
             {'title': u't', 'elements': [9, self.event.new_version_oid, 10]}),
            (IVersionable.__identifier__,
             {'follows': [self.child.__oid__]}),
        ])
        assert child_new_wanted_appstructs == child_new_appstructs

    def test_call_versionable_with_autoupdate_readonly(self):
        factory = self.config.registry.content.create
        self.event.isheet = IDummySheetAutoUpdate
        IDummySheetAutoUpdate.setTaggedValue('readonly', True)
        self._makeOne(self.event)
        assert not factory.called

    def test_call_versionable_with_autoupdate_readonly_other(self):
        factory = self.config.registry.content.create
        from adhocracy.sheets.versions import IVersionable
        self.event.isheet = IDummySheetAutoUpdate
        IDummySheetNoAutoUpdate.setTaggedValue('readonly', True)

        self._makeOne(self.event)

        assert factory.called
        child_new_parent = factory.call_args[1]['parent']
        child_new_appstructs = factory.call_args[1]['appstructs']
        assert child_new_parent is self.child.__parent__
        child_new_wanted_appstructs = dict([
            (IDummySheetAutoUpdate.__identifier__,
             {'title': u't', 'elements': [9, self.event.new_version_oid, 10]}),
            (IVersionable.__identifier__,
             {'follows': [self.child.__oid__]}),
        ])
        assert child_new_wanted_appstructs == child_new_appstructs

    def test_call_versionable_with_noautoupdate(self):
        factory = self.config.registry.content.create
        self.event.isheet = IDummySheetNoAutoUpdate
        self._makeOne(self.event)
        assert not factory.called

    @patch('adhocracy.resources.ResourceFactory', autospec=True)
    def test_call_nonversionable_with_autoupdate(self, dummyfactory=None):
        factory = dummyfactory.return_value
        from adhocracy.sheets.versions import IVersionable
        from zope.interface import noLongerProvides
        noLongerProvides(self.child, IVersionable)
        self.event.isheet = IDummySheetAutoUpdate

        self._makeOne(self.event)

        assert not factory.called
        child_wanted_appstruct = \
            {'title': u't', 'elements': [9, self.event.new_version_oid, 10]}
        key = IDummySheetAutoUpdate.__identifier__
        assert child_wanted_appstruct == self.child.dummy_appstruct[key]

    def test_call_noversionable_with_autoupdate_readonly(self):
        from adhocracy.sheets.versions import IVersionable
        from zope.interface import noLongerProvides
        noLongerProvides(self.child, IVersionable)
        self.event.isheet = IDummySheetAutoUpdate
        IDummySheetAutoUpdate.setTaggedValue('readonly', True)

        self._makeOne(self.event)

        child_wanted_appstruct = \
            {'title': u't', 'elements': [9, self.event.old_version_oid, 10]}
        key = IDummySheetAutoUpdate.__identifier__
        assert child_wanted_appstruct == self.child.dummy_appstruct[key]

    def test_call_noversionable_with_noautoupdate(self):
        from adhocracy.sheets.versions import IVersionable
        from zope.interface import noLongerProvides
        noLongerProvides(self.child, IVersionable)
        self.event.isheet = IDummySheetNoAutoUpdate

        self._makeOne(self.event)

        child_wanted_appstruct = \
            {'title': u't', 'elements': [9, self.event.old_version_oid, 10]}
        key = IDummySheetAutoUpdate.__identifier__
        assert child_wanted_appstruct == self.child.dummy_appstruct[key]


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.events')
        self.config.include('adhocracy.subscriber')

    def tearDown(self):
        testing.tearDown()

    def test_register_versions_adapter(self):
        from . import reference_has_new_version_subscriber
        handlers = [x.handler.__name__ for x
                    in self.config.registry.registeredHandlers()]
        assert len(handlers) >= 1
        assert reference_has_new_version_subscriber.__name__ in handlers
