import unittest
from copy import deepcopy

from pyramid import testing

from adhocracy_core.interfaces import ISheet


#############
#  helpers  #
#############

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


class ISheetA(ISheet):
    pass


class ISheetB(ISheet):
    pass


################
#  tests       #
################

class ResourceFactoryIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy_core.evolution')

    def tearDown(self):
        testing.tearDown()

    def test_includeme_add_directives(self):
        assert 'add_evolution_step' in self.config.registry._directives

from pytest import fixture


class TestMigrateNewSheet:

    @fixture
    def registry(self, registry_with_content, pool_sheet, a_sheet, b_sheet):
        from adhocracy_core.sheets.pool import IPool
        registry_with_content.content.get_sheet = lambda c, i: \
            i == IPool and pool_sheet \
            or i == ISheetA and a_sheet \
            or i == ISheetB and b_sheet
        return registry_with_content

    @fixture
    def pool_sheet(self, mock_sheet):
        return deepcopy(mock_sheet)

    @fixture
    def a_sheet(self, mock_sheet):
        return deepcopy(mock_sheet)

    @fixture
    def b_sheet(self, mock_sheet):
        return deepcopy(mock_sheet)

    @fixture
    def context(self, context):
        from zope.interface import alsoProvides
        from adhocracy_core.sheets.pool import IPool
        alsoProvides(context, ISheetB)
        alsoProvides(context, IPool)
        return context

    def call_fut(self, *args, **kwargs):
        from . import migrate_new_sheet
        return migrate_new_sheet(*args, **kwargs)

    def test_ignore_if_no_resources_without_new_isheet(
            self, context, registry, pool_sheet):
        from adhocracy_core.interfaces import IResource
        pool_sheet.get.return_value = {'elements': []}
        self.call_fut(context, IResource, ISheet, ISheetB)
        pool_sheet.get.assert_called_with({'interfaces': (ISheetB, IResource),
                                           'only_visible': False,
                                           })

    def test_add_new_isheet(self, context, registry, pool_sheet):
        from adhocracy_core.interfaces import IResource
        pool_sheet.get.return_value = {'elements': [context]}
        self.call_fut(context, IResource, ISheetA, ISheetB)
        assert ISheetA.providedBy(context)

    def test_remove_old_isheet(self, context, registry, pool_sheet):
        from adhocracy_core.interfaces import IResource
        pool_sheet.get.return_value = {'elements': [context]}
        self.call_fut(context, IResource, ISheetA, ISheetB,
                      remove_isheet_old=True)
        assert not ISheetB.providedBy(context)

    def test_copy_field_to_new_sheet(self, context, registry, pool_sheet,
                                     a_sheet, b_sheet):
        from adhocracy_core.interfaces import IResource
        pool_sheet.get.return_value = {'elements': [context]}
        b_sheet.get.return_value = {'field_b': 'value'}
        self.call_fut(context, IResource, ISheetA, ISheetB,
                      fields_mapping=[('field_a', 'field_b')])
        a_sheet.set.assert_called_with({'field_a': 'value'})

    def test_remove_old_field_values(self, context, registry, pool_sheet,
                                     a_sheet, b_sheet):
        from adhocracy_core.interfaces import IResource
        pool_sheet.get.return_value = {'elements': [context]}
        b_sheet.get.return_value = {'field_b': 'value'}
        self.call_fut(context, IResource, ISheetA, ISheetB,
                      fields_mapping=[('field_a', 'field_b')])
        b_sheet.delete_field_values.assert_called_with(['field_b'])

