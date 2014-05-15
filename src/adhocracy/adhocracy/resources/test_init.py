import unittest

from pyramid import testing
import pytest

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource


#############
#  helpers  #
#############

class ISheetY(ISheet):
    pass


class ISheetX(ISheet):
    pass


class DummyPropertySheetAdapter:

    readonly = False

    def __init__(self, context, iface):
        self.context = context
        self.iface = iface
        if not hasattr(self.context, 'dummy_appstruct'):
            self.context.dummy_appstruct = {}
        if not hasattr(self.context, 'dummy_cstruct'):
            self.context.dummy_cstruct = {}

    def set(self, appstruct):
        self.context.dummy_appstruct.update(appstruct)

    def get(self):
        return self.context.dummy_appstruct

    def set_cstruct(self, cstruct):
        self.context['dummy_cstruct'].update(cstruct)


def _register_dummypropertysheet_adapter(config):
    from adhocracy.interfaces import IResourcePropertySheet
    from adhocracy.interfaces import ISheet
    from zope.interface.interfaces import IInterface
    config.registry.registerAdapter(DummyPropertySheetAdapter,
                                    (ISheet, IInterface),
                                    IResourcePropertySheet)


class DummyFolder(testing.DummyResource):

    def add(self, name, obj, **kwargs):
        self[name] = obj
        obj.__name__ = name
        obj.__parent__ = self
        obj.__oid__ = 1

    def check_name(self, name):
        if name == 'invalid':
            raise ValueError
        return name

    def next_name(self, obj, prefix=''):
        return prefix + '_0000000'


###########
#  tests  #
###########


class ResourceFactoryUnitTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.base import Base
        from adhocracy.resources import resource_meta
        self.config = testing.setUp()
        self.context = DummyFolder()
        self.metadata = resource_meta._replace(iresource=IResource,
                                               content_class=Base)


    def tearDown(self):
        testing.tearDown()

    def make_one(self, metadata):
        from adhocracy.resources import ResourceFactory
        return ResourceFactory(metadata)

    def test_create(self):
        inst = self.make_one(self.metadata)
        assert '__call__' in dir(inst)

    def test_call_with_iresource(self):
        from zope.interface.verify import verifyObject
        from adhocracy.interfaces import IResource
        from zope.interface import directlyProvidedBy

        class IResourceX(IResource):
            pass
        meta = self.metadata._replace(iresource=IResourceX)

        inst = self.make_one(meta)()

        assert IResourceX in directlyProvidedBy(inst)
        assert verifyObject(IResourceX, inst)
        assert inst.__parent__ is None
        assert inst.__name__ == ''
        assert not hasattr(inst, '__oid__')

    def test_call_with_isheets(self):
        metadata = self.metadata._replace(basic_sheets=[ISheetY],
                                          extended_sheets=[ISheetX])
        inst = self.make_one(metadata)()

        assert ISheetX.providedBy(inst)
        assert ISheetY.providedBy(inst)

    def test_call_with_parent(self):
        meta = self.metadata
        inst = self.make_one(meta)(parent=self.context)

        assert inst.__parent__ == self.context
        assert inst.__name__ in self.context
        assert inst.__oid__ == 1

    def test_call_with_after_create(self):
        def dummy_after_create(context, registry, options):
            context._options = options
            context._registry = registry
        meta = self.metadata._replace(iresource=IResource,
                                      after_creation=[dummy_after_create])

        inst = self.make_one(meta)(kwarg1=True)

        assert inst._options == {'kwarg1': True}
        assert inst._registry is self.config.registry

    def test_call_without_run_after_create(self):
        def dummy_after_create(context, registry, options):
            context._options = options
            context._registry = registry
        meta = self.metadata._replace(iresource=IResource,
                                      after_creation=[dummy_after_create])

        inst = self.make_one(meta)(run_after_create=False)

        with pytest.raises(AttributeError):
            inst.test

    def test_call_with_appstructs_data(self):
        meta = self.metadata._replace(iresource=IResource,
                                      basic_sheets=[ISheetY])
        appstructs = {ISheetY.__identifier__: {'count': 0}}
        _register_dummypropertysheet_adapter(self.config)

        inst = self.make_one(meta)(appstructs=appstructs)

        assert inst.dummy_appstruct == {'count': 0}

    def test_call_with_parent_and_appstructs_name_data(self):
        meta = self.metadata._replace(iresource=IResource,
                                      basic_sheets=[ISheetY])
        appstructs = {'adhocracy.sheets.name.IName': {'name': 'child'}}
        _register_dummypropertysheet_adapter(self.config)

        self.make_one(meta)(parent=self.context, appstructs=appstructs)

        assert 'child' in self.context

    def test_call_with_parent_and_appstructs_empty_name_data(self):
        meta = self.metadata._replace(iresource=IResource,
                                      basic_sheets=[ISheetY])
        appstructs = {'adhocracy.sheets.name.IName': {'name': 'invalid'}}
        _register_dummypropertysheet_adapter(self.config)

        with pytest.raises(ValueError):
            self.make_one(meta)(parent=self.context, appstructs=appstructs)

    def test_call_with_parent_and_use_autonaming(self):
        meta = self.metadata._replace(iresource=IResource,
                                      use_autonaming=True)

        self.make_one(meta)(parent=self.context)

        assert '_0000000' in self.context

    def test_call_with_parent_and_use_autonaming_with_prefix(self):
        meta = self.metadata._replace(iresource=IResource,
                                      use_autonaming=True,
                                      autonaming_prefix='prefix')

        self.make_one(meta)(parent=self.context)

        assert 'prefix_0000000' in self.context
