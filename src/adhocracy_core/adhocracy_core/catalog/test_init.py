from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises

from adhocracy_core.interfaces import IPool


def test_create_adhocracy_catalog_indexes():
    from substanced.catalog import Keyword
    from adhocracy_core.catalog.adhocracy import AdhocracyCatalogIndexes
    from adhocracy_core.catalog.adhocracy import Reference
    inst = AdhocracyCatalogIndexes()
    assert isinstance(inst.tag, Keyword)
    assert isinstance(inst.reference, Reference)


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
def test_index_resource(pool_with_catalogs,):
    from substanced.util import find_service
    pool = pool_with_catalogs
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
    def inst(self, registry, meta, pool):
        from substanced.interfaces import MODE_IMMEDIATE
        inst = registry.content.create(meta.iresource.__identifier__,
                                       parent=pool)
        system = inst['system']
        system.action_mode = MODE_IMMEDIATE
        for index in system.values():
            index.action_mode = MODE_IMMEDIATE
        adhocracy = inst['adhocracy']
        adhocracy.action_mode = MODE_IMMEDIATE
        for index in adhocracy.values():
            index.action_mode = MODE_IMMEDIATE
        return inst

    @fixture
    def pool(self, pool_graph):
        return pool_graph

    def _make_resource(self, registry, parent=None, iresource=IPool):
        from datetime import datetime
        from adhocracy_core.sheets.name import IName
        appstructs = {}
        if IName in registry.content.resources_meta[iresource].basic_sheets:
            name = datetime.now().isoformat()
            appstructs = {IName.__identifier__: {'name': name}}
        return registry.content.create(iresource.__identifier__,
                                       parent=parent,
                                       appstructs=appstructs)

    def test_meta(self, meta):
        from substanced.catalog import CatalogsService
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

    def test_search_default_query_is_empty(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        result = inst.search(query)
        assert list(result.elements) == []

    def test_search_with_interface(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItemVersion
        missing_iresource = self._make_resource(registry, parent=pool)
        has_iresource = self._make_resource(registry, parent=pool,
                                            iresource=IItemVersion)
        result = inst.search(query._replace(interfaces=IItemVersion))
        assert list(result.elements) == [has_iresource]

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

    def test_search_with_interface_and_noteq(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItemVersion
        missing_iresource = self._make_resource(registry, parent=pool)
        has_iresource = self._make_resource(registry, parent=pool,
                                            iresource=IItemVersion)
        result = inst.search(query._replace(interfaces=('noteq', IItemVersion)))
        elements = list(result.elements)
        assert has_iresource not in elements
        assert missing_iresource in elements

    def test_search_with_interfaces_and_notany(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ISimple
        from adhocracy_core.interfaces import IItemVersion
        from adhocracy_core.sheets.versions import IVersionable
        has_isheet = self._make_resource(registry, parent=pool,
                                         iresource=ISimple)
        has_iresource = self._make_resource(registry, parent=pool,
                                            iresource=IItemVersion)
        missing_iresource = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=('notany',
                                                        (IVersionable,
                                                         ISimple))))
        elements = list(result.elements)
        assert has_isheet not in elements
        assert has_iresource not in elements
        assert missing_iresource in elements

    def test_search_with_interfaces_raise_if_wrong_keyword_index_comparator(
            self, registry, pool, inst, query):
        from adhocracy_core.sheets.versions import IVersionable
        with raises(AttributeError):
            inst.search(query._replace(interfaces=('gt', (IVersionable,))))

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
        elements = list(result.elements)
        assert child in elements
        assert grandchild not in elements

    def test_search_with_root_and_depth2(self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        grandchild = self._make_resource(registry, parent=child)
        result = inst.search(query._replace(root=pool,
                                            depth=2))
        elements = list(result.elements)
        assert child in elements
        assert grandchild in elements

    def test_search_with_resolve(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IPool
        child = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            resolve=True))
        assert result.elements == [child]

    def test_search_with_only_visible(self, registry, pool, inst, query):
        from adhocracy_core.sheets.metadata import IMetadata
        child_hidden = self._make_resource(registry, parent=pool)
        meta_sheet = registry.content.get_sheet(child_hidden, IMetadata)
        meta_sheet.set({'hidden': True})
        child_visible = self._make_resource(registry, parent=pool)
        meta_sheet = registry.content.get_sheet(child_visible, IMetadata)
        meta_sheet.set({'hidden': False})
        result = inst.search(query._replace(only_visible=True))
        elements = list(result.elements)
        assert child_visible in elements
        assert child_hidden not in elements

    def test_search_with_indexes(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItem
        item = self._make_resource(registry, parent=pool, iresource=IItem)
        has_tag = item['VERSION_0000000']
        result = inst.search(query._replace(indexes={'tag': 'FIRST'}))
        assert list(result.elements) == [has_tag]

    def test_search_with_indexes_and_noteq(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItem
        item = self._make_resource(registry, parent=pool, iresource=IItem)
        has_tag = item['VERSION_0000000']
        missing_tag = item
        result = inst.search(query._replace(
            indexes={'tag': ('noteq', 'FIRST')}))
        elements = list(result.elements)
        assert has_tag not in elements
        assert missing_tag in elements

    def test_search_with_indexes_and_any(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItem
        item = self._make_resource(registry, parent=pool, iresource=IItem)
        has_tag = item['VERSION_0000000']
        missing_tag = item
        result = inst.search(query._replace(
            indexes={'tag': ('any', ('FIRST', 'LAST'))}))
        elements = list(result.elements)
        assert has_tag in elements
        assert missing_tag not in elements

    def test_search_with_indexes_and_any(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItem
        item = self._make_resource(registry, parent=pool, iresource=IItem)
        has_tag = item['VERSION_0000000']
        missing_tag = item
        result = inst.search(query._replace(
            indexes={'tag': ('notany', ('FIRST', 'LAST'))}))
        elements = list(result.elements)
        assert has_tag not in elements
        assert missing_tag in elements

    def test_search_with_references(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItem
        from adhocracy_core.interfaces import Reference
        from adhocracy_core import sheets
        referenced = pool
        referencing = self._make_resource(registry, parent=pool,
                                          iresource=IItem)
        sheet = registry.content.get_sheet(referencing, sheets.tags.ITags)
        sheet.set({'FIRST': referenced})
        reference = Reference(None, sheets.tags.ITags, 'FIRST', referenced)
        result = inst.search(query._replace(references=[reference]))
        assert list(result.elements) == [referencing]

    def test_search_with_two_references(self, registry, pool, service, inst,
                                        query):
        from copy import deepcopy
        from adhocracy_core.interfaces import Reference
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core import sheets
        pool['principals'] = service
        pool['principals']['groups'] = deepcopy(service)
        user = self._make_resource(registry, parent=pool, iresource=IUser)
        referencing = self._make_resource(registry, parent=pool)
        sheet = registry.content.get_sheet(referencing, sheets.metadata.IMetadata)
        sheet.set({'creator': [user]})
        reference = Reference(None, sheets.metadata.IMetadata,
                              'creator', user)
        result = inst.search(query._replace(references=[reference, reference]))
        elements = list(result.elements)
        assert elements == [user]

    def test_search_with_references_include_isheet_subtypes(
            self, registry, pool, inst, query):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import IItem
        from adhocracy_core.interfaces import Reference
        from adhocracy_core import sheets
        referenced = pool
        referencing = self._make_resource(registry, parent=pool,
                                          iresource=IItem)
        sheet = registry.content.get_sheet(referencing, sheets.tags.ITags)
        sheet.set({'FIRST': referenced})
        reference = Reference(None, ISheet, 'FIRST', referenced)
        result = inst.search(query._replace(references=[reference]))
        assert list(result.elements) == [referencing]

    def test_search_with_references_ignore_field_name_if_empty(
            self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItem
        from adhocracy_core.interfaces import Reference
        from adhocracy_core import sheets
        referenced = pool
        referencing = self._make_resource(registry, parent=pool,
                                          iresource=IItem)
        sheet = registry.content.get_sheet(referencing, sheets.tags.ITags)
        sheet.set({'FIRST': referenced})
        reference = Reference(None, sheets.tags.ITags, '', referenced)
        result = inst.search(query._replace(references=[reference]))
        assert list(result.elements) == [referencing]

    def test_search_with_back_references(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IItem
        from adhocracy_core.interfaces import Reference
        from adhocracy_core import sheets
        referenced1 = self._make_resource(registry, parent=pool)
        referenced2 = self._make_resource(registry, parent=pool)
        referenced3 = self._make_resource(registry, parent=pool)
        referencing = self._make_resource(registry, parent=pool,
                                          iresource=IItem)
        sheet = registry.content.get_sheet(referencing, sheets.tags.ITags)
        sheet.set({'LAST': [referenced3, referenced1, referenced2]})
        reference = Reference(referencing, sheets.tags.ITags, 'LAST', None)
        result = inst.search(query._replace(references=[reference]))
        elements = list(result.elements)
        assert len(elements) == 3  # search for back references is not ordered
        assert referenced1 in elements
        assert referenced2 in elements
        assert referenced3 in elements

    def test_search_with_back_reference_traverse(self, registry, pool, service,
                                                 inst, query):
        from adhocracy_core.interfaces import Reference
        from adhocracy_core.interfaces import ReferenceComparator
        from adhocracy_core.resources.comment import IComment
        from adhocracy_core.resources.comment import ICommentVersion
        from adhocracy_core.resources.comment import ICommentsService
        from adhocracy_core import sheets
        registry.content.create(ICommentsService.__identifier__,
                                parent=pool)
        comments = pool['comments']
        comment = self._make_resource(registry, parent=comments, iresource=IComment)
        referencing = self._make_resource(registry, parent=comment,
                                          iresource=ICommentVersion)
        referenced1 = self._make_resource(registry, parent=comment,
                                          iresource=ICommentVersion)
        referenced2 = self._make_resource(registry, parent=comment,
                                          iresource=ICommentVersion)
        sheet = registry.content.get_sheet(referencing, sheets.comment.IComment)
        sheet.set({'refers_to': referenced1})
        sheet = registry.content.get_sheet(referenced1, sheets.comment.IComment)
        sheet.set({'refers_to': referenced2})
        reference = Reference(referencing, sheets.comment.IComment,
                              'refers_to', None)
        result = inst.search(query._replace(
                references=[(ReferenceComparator.traverse.value, reference)]))
        elements = list(result.elements)
        assert len(elements) == 2  # search with traversal is not ordered
        assert referenced1 in elements
        assert referenced2 in elements

    def test_search_with_sort_by(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IPool
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            sort_by='name'))
        assert list(result.elements) == [child, child2]

    def test_search_with_sort_by_and_reverse(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IPool
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            sort_by='name',
                                            reverse=True))
        assert list(result.elements) == [child2, child]

    def test_search_with_sort_by_raise_if_index_not_sortable(
            self, registry, pool, inst, query):
        child = self._make_resource(registry, parent=pool)
        with raises(AssertionError):
            inst.search(query._replace(sort_by='interfaces'))

    def test_search_with_limit(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IPool
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            limit=1))
        assert list(result.elements) == [child]

    def test_search_with_limit_and_offset(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IPool
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            limit=2,
                                            offset=1))
        assert list(result.elements) == [child2]

    def test_search_with_frequency_of(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IResource
        child = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IResource,
                                            frequency_of='interfaces'))
        assert result.frequency_of[IResource] == 1

    def test_search_with_sort_by_reference_ignore_if_no_references(
            self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IPool
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            sort_by='reference'))
        assert list(result.elements) == [child, child2]

    def test_search_with_sort_by_references(self, registry, pool, inst, query):
        """Use the first reference (not back reference) to sort."""
        from hypatia.util import ResultSet
        from adhocracy_core.interfaces import Reference
        from adhocracy_core.interfaces import ISheet
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        search_result = ResultSet((child.__oid__, child2.__oid__), 2, None)
        inst._search_elements = Mock(return_value=search_result)
        references_result = ResultSet((child2.__oid__, child.__oid__), 2, None)
        reference_index = inst['adhocracy']['reference']
        reference_index.search_with_order = Mock(return_value=
                                                 references_result)
        reference = Reference(child, ISheet, 'field', None)
        back_reference = Reference(None, ISheet, 'field', child2)
        result = inst.search(query._replace(interfaces=IPool,
                                            references=(back_reference,
                                                        reference),
                                            sort_by='reference'))
        reference_index.search_with_order.assert_called_once_with(reference)
        assert list(result.elements) == [child2, child]

    def test_search_with_sort_by_references_and_reverse(self, registry, pool,
                                                        inst, query):
        from adhocracy_core.interfaces import Reference
        from adhocracy_core.interfaces import ISheet
        child = self._make_resource(registry, parent=pool)
        reference = Reference(child, ISheet, 'field', None)
        with raises(NotImplementedError):
            inst.search(query._replace(interfaces=IPool,
                                       references=(reference,),
                                       sort_by='reference',
                                       reverse=True))

    def test_search_with_sort_by_references_and_limit(self, registry, pool,
                                                      inst, query):
        from adhocracy_core.interfaces import Reference
        from adhocracy_core.interfaces import ISheet
        child = self._make_resource(registry, parent=pool)
        reference = Reference(child, ISheet, 'field', None)
        with raises(NotImplementedError):
            inst.search(query._replace(interfaces=IPool,
                                       references=(reference,),
                                       sort_by='reference',
                                       limit=10))

    def test_search_with_group_by(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IPool
        child = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            group_by='interfaces',
                                            resolve=True))
        assert list(result.group_by[IPool]) == [child]

    def test_search_with_group_by_and_resolve_false(self, registry, pool, inst,
                                                    query):
        from adhocracy_core.interfaces import IPool
        from collections.abc import Iterable
        child = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            group_by='interfaces',
                                            resolve=False))
        assert isinstance(result.group_by[IPool], Iterable)

    def test_search_with_group_by_and_sort_by(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IPool
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            group_by='interfaces',
                                            sort_by='name'))
        assert list(result.group_by[IPool]) == [child, child2]

    def test_search_with_allows_no_permission(self, registry, pool, inst, query):
        from adhocracy_core.interfaces import IPool
        from pyramid.authorization import Deny
        from adhocracy_core.authorization import set_acl
        child = self._make_resource(registry, parent=pool)
        set_acl(pool, [(Deny, 'principal', 'view')], registry)
        inst['system']['allowed'].reindex_resource(child)
        result = inst.search(query._replace(interfaces=IPool,
                                            allows=(['principal'], 'view')))
        assert list(result.elements) == []

    def test_search_with_allows_has_permission(self, registry, pool, inst,
                                               query):
        from adhocracy_core.interfaces import IPool
        from pyramid.authorization import Allow
        from adhocracy_core.authorization import set_acl
        child = self._make_resource(registry, parent=pool)
        set_acl(pool, [(Allow, 'principal', 'view')], registry)
        inst['system']['allowed'].reindex_resource(child)
        result = inst.search(query._replace(interfaces=IPool,
                                            allows=(['principal'], 'view')))
        assert list(result.elements) == [child]

    def test_search_count_with_limit_and_sort(self, registry, pool, inst,
                                              query):
        from adhocracy_core.interfaces import IPool
        child = self._make_resource(registry, parent=pool)
        child2 = self._make_resource(registry, parent=pool)
        result = inst.search(query._replace(interfaces=IPool,
                                            limit=1,
                                            sort_by='name'))
        assert result.count == 2

    def test_get_index_value(selfs, registry, inst, mocker):
        context = Mock()
        index = Mock()
        oid = Mock()
        get_oid = mocker.patch('adhocracy_core.catalog.get_oid',
                               return_value=oid)
        inst.get_index = Mock(return_value=index)
        result = inst.get_index_value(context, 'value')
        get_oid.assert_called_with(context)
        index.document_repr.asser_called_with(oid)
        assert result == index.document_repr()
