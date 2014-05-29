import unittest

from mock import patch
from pyramid import testing
import pytest

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import sheet_metadata


#############
#  helpers  #
#############

class ISheetY(ISheet):
    pass


class ISheetX(ISheet):
    pass


@patch('adhocracy.sheets.GenericResourceSheet')
def _create_dummy_sheet_adapter(registry, isheet, sheet_dummy=None):
    from adhocracy.interfaces import IResourceSheet
    registry.registerAdapter(sheet_dummy, (isheet,),
                             IResourceSheet,
                             isheet.__identifier__)
    return sheet_dummy


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



class AddResourceTypeIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.interfaces import resource_metadata
        from adhocracy.resources.resource import Base
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.content_registry = self.config.registry.content
        self.resource_metadata = resource_metadata._replace(iresource=IResource,
                                                            content_class=Base)

    def tearDown(self):
        testing.tearDown()

    def make_one(self, *args):
        from adhocracy.resources import add_resource_type_to_registry
        return add_resource_type_to_registry(*args)

    def test_add_iresource_but_missing_content_registry(self):
        del self.config.registry.content
        with pytest.raises(AssertionError):
            self.make_one(self.resource_metadata, self.config)

    def test_add_resource_type(self):
        self.make_one(self.resource_metadata, self.config)
        resource = self.content_registry.create(IResource.__identifier__)
        assert IResource.providedBy(resource)

    def test_add_resource_type_metadata(self):
        type_id = IResource.__identifier__
        self.make_one(self.resource_metadata, self.config)
        assert self.content_registry.meta[type_id]['content_name'] == type_id
        assert self.content_registry.meta[type_id]['resource_metadata']\
            == self.resource_metadata

    def test_add_resource_type_metadata_with_content_name(self):
        type_id = IResource.__identifier__
        metadata_a = self.resource_metadata._replace(content_name='Name')
        self.make_one(metadata_a, self.config)
        assert self.content_registry.meta[type_id]['content_name'] == 'Name'


class ResourceFactoryUnitTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.resources.resource import Base
        from adhocracy.resources.resource import resource_metadata
        self.config = testing.setUp()
        self.context = DummyFolder()
        self.metadata = resource_metadata._replace(iresource=IResource,
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

    def test_call_with_creatable_appstructs_data(self):
        meta = self.metadata._replace(iresource=IResource,
                                      basic_sheets=[ISheetY])
        dummy_sheet = _create_dummy_sheet_adapter(self.config.registry, ISheetY)
        dummy_sheet.return_value.meta = sheet_metadata._replace(creatable=True)
        appstructs = {ISheetY.__identifier__: {'count': 0}}

        self.make_one(meta)(appstructs=appstructs)

        assert dummy_sheet.return_value.set.called

    def test_call_with_not_creatable_appstructs_data(self):
        meta = self.metadata._replace(iresource=IResource,
                                      basic_sheets=[ISheetY])
        dummy_sheet = _create_dummy_sheet_adapter(self.config.registry, ISheetY)
        dummy_sheet.return_value.meta = sheet_metadata._replace(creatable=False)
        appstructs = {ISheetY.__identifier__: {'count': 0}}

        self.make_one(meta)(appstructs=appstructs)

        assert not dummy_sheet.return_value.set.called

    def test_call_with_parent_and_appstructs_name_data(self):
        from adhocracy.sheets.name import IName
        meta = self.metadata._replace(iresource=IResource,
                                      basic_sheets=[IName])
        dummy_sheet = _create_dummy_sheet_adapter(self.config.registry, IName)
        dummy_sheet.return_value.set.return_value = False
        appstructs = {IName.__identifier__: {'name': 'child'}}

        self.make_one(meta)(parent=self.context, appstructs=appstructs)

        assert 'child' in self.context
        assert dummy_sheet.return_value.set.called

    def test_call_with_parent_and_appstructs_empty_name_data(self):
        meta = self.metadata._replace(iresource=IResource,
                                      basic_sheets=[ISheetY])
        appstructs = {'adhocracy.sheets.name.IName': {'name': 'invalid'}}
        _create_dummy_sheet_adapter(self.config.registry, ISheetY)

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
