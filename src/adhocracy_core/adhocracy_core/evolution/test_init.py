from copy import deepcopy
from pyramid import testing
from pytest import fixture
from unittest.mock import Mock
from unittest.mock import call
import unittest

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
    def context(self, pool, mock_catalogs):
        from zope.interface import alsoProvides
        alsoProvides(pool, ISheetB)
        pool['catalogs'] = mock_catalogs
        return pool

    def call_fut(self, *args, **kwargs):
        from . import migrate_new_sheet
        return migrate_new_sheet(*args, **kwargs)

    def test_ignore_if_no_resources_to_migrate(
            self, context, mock_catalogs, search_result, query):
        from adhocracy_core.interfaces import IResource
        mock_catalogs.search.return_value = search_result
        self.call_fut(context, IResource, ISheetB)

    def test_add_new_isheet(self, context, mock_catalogs, search_result, query):
        from adhocracy_core.interfaces import IResource
        mock_catalogs.search.return_value = search_result._replace(
            elements=[context])
        self.call_fut(context, IResource, ISheetA)
        assert ISheetA.providedBy(context)
        search_query = query._replace(interfaces=(IResource))
        assert mock_catalogs.search.call_args[0][0] == search_query

    def test_remove_old_isheet(self, context, mock_catalogs, search_result):
        from adhocracy_core.interfaces import IResource
        mock_catalogs.search.return_value = search_result._replace(
            elements=[context])
        self.call_fut(context, IResource, ISheetA,
                      isheet_old=ISheetB,
                      remove_isheet_old=True)
        assert not ISheetB.providedBy(context)

    def test_copy_field_to_new_sheet(self, context, registry, mock_catalogs,
                                     search_result, a_sheet, b_sheet):
        from adhocracy_core.interfaces import IResource
        mock_catalogs.search.return_value = search_result._replace(
            elements=[context])
        b_sheet.get.return_value = {'field_b': 'value'}
        self.call_fut(context, IResource, ISheetA, ISheetB,
                      fields_mapping=[('field_a', 'field_b')])
        a_sheet.set.assert_called_with({'field_a': 'value'})

    def test_remove_old_field_values(self, context, registry,  mock_catalogs,
                                     search_result, a_sheet, b_sheet):
        from adhocracy_core.interfaces import IResource
        mock_catalogs.search.return_value = search_result._replace(
            elements=[context])
        b_sheet.get.return_value = {'field_b': 'value'}
        self.call_fut(context, IResource, ISheetA, ISheetB,
                      fields_mapping=[('field_a', 'field_b')])
        b_sheet.delete_field_values.assert_called_with(['field_b'])


class TestLogMigrationDecorator:

    def test_log_migration_decorator_call(self, monkeypatch):
        from . import log_migration
        mock_func = Mock()

        @log_migration
        def evolve():
            """doc."""
            mock_func()

        evolve()

        assert mock_func.called

    def test_log_migration_decorator_call_with_args(self, monkeypatch):
        from . import log_migration
        mock_func = Mock()

        @log_migration
        def evolve(i):
            """doc."""
            mock_func(i)

        evolve(1)

        assert mock_func.called

    def test_log_migration_decorator_log(self, monkeypatch):
        import adhocracy_core.evolution
        from . import log_migration
        mock_logger = Mock()
        monkeypatch.setattr(adhocracy_core.evolution, 'logger', mock_logger)

        @log_migration
        def evolve():
            """Somedoc."""
            pass

        return evolve
 
        mock_logger.info.assert_has_calls([call('Running evolve step: Somedoc.'),
                                           call('Finished evolve step: Somedoc.')])

    def test_log_migration_decorator_keep_func_attributes(self):
        from . import log_migration

        @log_migration
        def f():
            pass

        assert f.__name__ is 'f'
