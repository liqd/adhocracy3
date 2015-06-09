import unittest
from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


def test_create_adhocracy_catalog_indexes():
    from substanced.catalog import Keyword
    from adhocracy_core.catalog.adhocracy import AdhocracyCatalogIndexes
    from adhocracy_core.catalog.adhocracy import Reference
    inst = AdhocracyCatalogIndexes()
    assert isinstance(inst.tag, Keyword)
    assert isinstance(inst.reference, Reference)


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.pool')
    config.include('adhocracy_core.resources.simple')
    config.include('adhocracy_core.resources.itemversion')
    config.include('adhocracy_core.resources.item')
    config.include('adhocracy_core.resources.tag')


@mark.usefixtures('integration')
def test_create_adhocracy_catalog(pool_graph, registry):
    from substanced.catalog import Catalog
    from adhocracy_core.catalog import ICatalogsService
    catalogs = registry.content.create(ICatalogsService.__identifier__,
                                       parent=pool_graph)
    assert isinstance(catalogs['adhocracy'], Catalog)
    assert 'tag' in catalogs['adhocracy']
    assert 'reference' in catalogs['adhocracy']
    assert 'rate' in catalogs['adhocracy']
    assert 'rates' in catalogs['adhocracy']
    assert 'creator' in catalogs['adhocracy']


@mark.usefixtures('integration')
def test_add_indexing_adapter():
    from substanced.interfaces import IIndexingActionProcessor
    assert IIndexingActionProcessor(object()) is not None


@mark.usefixtures('integration')
def test_add_directives(registry):
    assert 'add_catalog_factory' in registry._directives
    assert 'add_indexview' in registry._directives


@mark.usefixtures('integration')
def test_index_resource(pool_graph_catalog,):
    from substanced.util import find_service
    pool = pool_graph_catalog
    pool.add('child', testing.DummyResource())
    name_index = find_service(pool, 'catalogs', 'system', 'name')
    assert 'child' in [x for x in name_index.unique_values()]


@mark.usefixtures('integration')
class TestCatalogsServiceAdhocracy:

    @fixture
    def meta(self):
        from . import catalogs_service_meta
        return catalogs_service_meta

    @fixture
    def inst(self, registry, meta, pool_graph):
        from substanced.interfaces import MODE_IMMEDIATE
        inst = registry.content.create(meta.iresource.__identifier__,
                                       parent=pool_graph)
        inst['system']['name'].action_mode = MODE_IMMEDIATE
        inst['system']['interfaces'].action_mode = MODE_IMMEDIATE
        inst['system']['allowed'].action_mode = MODE_IMMEDIATE
        inst['adhocracy']['tag'].action_mode = MODE_IMMEDIATE
        return inst

    @fixture
    def pool(self, pool_graph):
        return pool_graph

    def _make_resource(self, registry, parent=None, iresource=None):
        from datetime import datetime
        from adhocracy_core.interfaces import IPool
        from adhocracy_core.sheets.name import IName
        if iresource is None:
            iresource = IPool
        appstructs = {}
        if IName in registry.content.resources_meta[iresource].basic_sheets:
            name = datetime.now().isoformat()
            appstructs = {IName.__identifier__: {'name': name}}
        return registry.content.create(iresource.__identifier__,
                                       parent=parent,
                                       appstructs=appstructs)

    def test_meta(self, meta):
        from substanced.catalog import CatalogsService
        from adhocracy_core.interfaces import IServicePool
        from . import ICatalogsService
        from . import CatalogsServiceAdhocracy
        assert meta.iresource is ICatalogsService
        assert meta.content_name == 'catalogs'
        assert meta.permission_create == 'create_service'
        assert meta.content_class == CatalogsServiceAdhocracy
        assert issubclass(CatalogsServiceAdhocracy, CatalogsService)

    def test_create(self, pool_graph, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool_graph)
        assert meta.iresource.providedBy(res)
        assert 'adhocracy' in res
        assert 'system' in res

    def test_reindex_all(self, registry, pool, inst):
        from hypatia.catalog import Catalog
        inst['adhocracy'].reindex_resource = Mock()
        inst['system'].reindex_resource = Mock()
        child = self._make_resource(registry, parent=pool)
        inst.reindex_all(child)
        inst['adhocracy'].reindex_resource.assert_called_with(child)
        inst['system'].reindex_resource.assert_called_with(child)

    def test_reindex_index(self, registry, pool, inst):
        inst['adhocracy']['rate'].reindex_resource = Mock()
        child = self._make_resource(registry, parent=pool)
        inst.reindex_index(child, 'rate')
        inst['adhocracy']['rate'].reindex_resource.assert_called_with(child)

    def test_reindex_index_raise_if_wrong_index(self, registry, pool, inst):
        from hypatia.field import FieldIndex
        inst['adhocracy']['rate'].reindex_resource = Mock(spec=FieldIndex)
        child = self._make_resource(registry, parent=pool)
        with raises(KeyError):
            inst.reindex_index(child, 'WRONG')

    def test_search_default_query(self, registry, pool, inst, query):
        from hypatia.interfaces import IResultSet
        child = self._make_resource(registry, parent=pool)
        result = inst.search(query)
        assert IResultSet.providedBy(result.elements)
        assert list(result.elements) == [child]

    def test_search_count_result_elements(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        result = inst.search(query)
        assert result.count == 1

    def test_search_with_interface(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItemVersion
        missing_iresource = self._make_resource(registry, parent=pool)
        right = self._make_resource(registry, parent=pool,
                                    iresource=IItemVersion)
        result = inst.search(query._replace(interfaces=(IItemVersion,)))
        assert list(result.elements) == [right]

    def test_search_with_interfaces(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ISimple
        from adhocracy_core.interfaces import IItemVersion
        from adhocracy_core.sheets.versions import IVersionable
        missing_isheet = self._make_resource(registry, parent=pool,
                                             iresource=ISimple)
        missing_iresource = self._make_resource(registry, parent=pool,
                                                iresource=IItemVersion)
        result = inst.search(query._replace(interfaces=(IVersionable, ISimple)))
        assert list(result.elements) == []

    def test_search_with_root_return_all_descendants(self, registry, pool, inst,
                                                     query):
        parent1 = self._make_resource(registry, parent=pool)
        parent1_child = self._make_resource(registry, parent=parent1)
        parent1_grandchild = self._make_resource(registry, parent=parent1_child)
        parent2 = self._make_resource(registry, parent=pool)
        parent2_child = self._make_resource(registry, parent=parent2)
        result = inst.search(query._replace(root=parent1))
        assert list(result.elements) == [parent1_child, parent1_grandchild]

    def test_search_with_root_and_depth1(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        grandchild = self._make_resource(registry, parent=child)
        result = inst.search(query._replace(root=pool,
                                            depth=1))
        assert list(result.elements) == [child]

    def test_search_with_root_and_depth2(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        grandchild = self._make_resource(registry, parent=child)
        result = inst.search(query._replace(root=pool,
                                            depth=2))
        assert list(result.elements) == [child, grandchild]

    def test_search_with_resolve(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(resolve=True))
        assert result.elements == [child]

    def test_search_with_only_visible(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        child.hidden = True
        inst['adhocracy']['private_visibility'].reindex_resource(child)
        result = inst.search(query._replace(only_visible=True))
        assert list(result.elements) == []

    def test_search_with_only_visible_false(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        child.hidden = True
        inst['adhocracy']['private_visibility'].reindex_resource(child)
        result = inst.search(query._replace(only_visible=False))
        assert list(result.elements) == [child]

    def test_search_with_indexes(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItem
        item = self._make_resource(registry, parent=pool, iresource=IItem)
        first = item['VERSION_0000000']
        result = inst.search(query._replace(indexes={'tag': 'FIRST'}))
        assert list(result.elements) == [first]

    def test_search_with_references(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ITag
        from adhocracy_core.interfaces import Reference
        from adhocracy_core import sheets
        from adhocracy_core.utils import get_sheet
        referenced = pool
        referencing = self._make_resource(registry, parent=pool, iresource=ITag)
        sheet = get_sheet(referencing, sheets.tags.ITag)
        sheet.set({'elements': [referenced]})
        reference = Reference(None, sheets.tags.ITag, 'elements', referenced)
        result = inst.search(query._replace(references=[reference]))
        assert list(result.elements) == [referencing]

    def test_search_with_references_include_isheet_subtypes(
            self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import ITag
        from adhocracy_core.interfaces import Reference
        from adhocracy_core import sheets
        from adhocracy_core.utils import get_sheet
        referenced = pool
        referencing = self._make_resource(registry, parent=pool,
                                          iresource=ITag)
        sheet = get_sheet(referencing, sheets.tags.ITag)
        sheet.set({'elements': [referenced]})
        reference = Reference(None, ISheet, 'elements', referenced)
        result = inst.search(query._replace(references=[reference]))
        assert list(result.elements) == [referencing]

    def test_search_with_references_ignore_field_name_if_empty(
            self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ITag
        from adhocracy_core.interfaces import Reference
        from adhocracy_core import sheets
        from adhocracy_core.utils import get_sheet
        referenced = pool
        referencing = self._make_resource(registry, parent=pool,
                                          iresource=ITag)
        sheet = get_sheet(referencing, sheets.tags.ITag)
        sheet.set({'elements': [referenced]})
        reference = Reference(None, sheets.tags.ITag, '', referenced)
        result = inst.search(query._replace(references=[reference]))
        assert list(result.elements) == [referencing]

    def test_search_with_back_references(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ITag
        from adhocracy_core.interfaces import Reference
        from adhocracy_core import sheets
        from adhocracy_core.utils import get_sheet
        referenced = self._make_resource(registry, parent=pool)
        referencing = self._make_resource(registry, parent=pool, iresource=ITag)
        sheet = get_sheet(referencing, sheets.tags.ITag)
        sheet.set({'elements': [referenced]})
        reference = Reference(referencing, sheets.tags.ITag, 'elements', None)
        result = inst.search(query._replace(references=[reference]))
        assert list(result.elements) == [referenced]

    def test_search_with_sort_by(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(sort_by='name'))
        assert list(result.elements) == [child, child2]

    def test_search_with_sort_by_and_reverse(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(sort_by='name',
                                            reverse=True))
        assert list(result.elements) == [child2, child]

    def test_search_with_sort_by_raise_if_index_not_sortable(
            self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        with raises(AssertionError):
            inst.search(query._replace(sort_by='interfaces'))

    def test_search_with_limit(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(limit=1))
        assert list(result.elements) == [child]

    def test_search_with_limit_and_offset(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(limit=2,
                                            offset=1))
        assert list(result.elements) == [child2]

    def test_search_with_frequency_of(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ISimple
        child = self._make_resource(registry, parent=pool, iresource=ISimple)
        result = inst.search(query._replace(frequency_of='interfaces'))
        assert result.frequency_of[ISimple] == 1

    def test_search_with_group_by(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ISimple
        child = self._make_resource(registry, parent=pool, iresource=ISimple)
        result = inst.search(query._replace(group_by='interfaces'))
        assert list(result.group_by[ISimple]) == [child]

    def test_search_with_group_by_and_resolve_false(self, registry, pool, inst,
                                                    query):
        from adhocracy_core.interfaces import ISimple
        from hypatia.interfaces import IResultSet
        child = self._make_resource(registry, parent=pool, iresource=ISimple)
        result = inst.search(query._replace(group_by='interfaces',
                                            resolve=False))
        assert IResultSet.providedBy(result.group_by[ISimple])

    def test_search_with_group_by_and_sort_by(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ISimple
        child = self._make_resource(registry, parent=pool, iresource=ISimple)
        child2 = self._make_resource(registry, parent=pool, iresource=ISimple)
        result = inst.search(query._replace(group_by='interfaces',
                                            sort_by='name'))
        assert list(result.group_by[ISimple]) == [child, child2]

    def test_search_with_allows_no_permission(self, registry, pool, inst, query):
        from pyramid.authorization import Deny
        from adhocracy_core.authorization import set_acl
        child = self._make_resource(registry, parent=pool)
        set_acl(pool, [(Deny, 'principal', 'view')], registry=registry)
        inst['system']['allowed'].reindex_resource(child)
        result = inst.search(query._replace(allows=(['principal'], 'view')))
        assert list(result.elements) == []

    def test_search_with_allows_has_permission(self, registry, pool, inst,
                                               query):
        from pyramid.authorization import Allow
        from adhocracy_core.authorization import set_acl
        child = self._make_resource(registry, parent=pool)
        set_acl(pool, [(Allow, 'principal', 'view')], registry=registry)
        inst['system']['allowed'].reindex_resource(child)
        result = inst.search(query._replace(allows=(['principal'], 'view')))
        assert list(result.elements) == [child]

