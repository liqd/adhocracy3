from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises

from adhocracy_core.resources.pool import IBasicPool

import itertools

@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.resources.pool')
    config.include('adhocracy_core.resources.tag')
    config.include('adhocracy_core.resources.item')
    config.include('adhocracy_core.resources.itemversion')
    config.include('adhocracy_core.sheets')


class TestPoolSchema:

    @fixture
    def request(self, cornice_request):
        return cornice_request

    def make_one(self):
        from .pool import PoolSchema
        return PoolSchema()

    def test_serialize_empty(self):
        inst = self.make_one()
        assert inst.serialize() == {'elements': []}

    def test_serialize_empty_with_count_request_param(self, request):
        request.validated['count'] = True
        inst = self.make_one().bind(request=request)
        assert inst.serialize() == {'elements': [],
                                    'count': '0'}

    def test_serialize_empty_with_aggregateby_request_param(self, request):
        request.validated['aggregateby'] = 'index1'
        inst = self.make_one().bind(request=request)
        assert inst.serialize() == {'elements': [],
                                    'aggregateby': {}}


class TestFilteringPoolSheet:

    @fixture
    def request(self, cornice_request, registry_with_content):
        cornice_request.registry = registry_with_content
        return cornice_request

    @fixture
    def meta(self):
        from adhocracy_core.sheets.pool import pool_meta
        return pool_meta

    @fixture
    def filter_elements_result(self):
        from adhocracy_core.sheets.pool import FilterElementsResult
        return FilterElementsResult(['Dummy'], 1, {})

    @fixture
    def mock_filter_elements(self, meta, filter_elements_result):
        mock = Mock(spec=meta.sheet_class._filter_elements)
        mock.return_value = filter_elements_result
        return mock

    @fixture
    def inst(self, meta, context, mock_filter_elements):
        inst = meta.sheet_class(meta, context)
        inst._filter_elements = mock_filter_elements
        return inst

    @fixture
    def filter_elements_kwargs(self):
        """Return default kwargs for the _filter_elements method."""
        from adhocracy_core.interfaces import ISheet
        default_kwargs = {'depth': 1,
                          'ifaces': [ISheet],
                          'arbitrary_filters': {},
                          'resolve_resources': True,
                          'references': {},
                          'sort_filter': '',
                          'reverse': False,
                          'limit': None,
                          'offset': 0,
                          'aggregate_filter': '',
                          'aggregate_form': 'count',
                          'only_visible': True,
                          }
        return default_kwargs

    def test_create(self, context, meta):
        from adhocracy_core.sheets.pool import pool_meta
        inst = pool_meta.sheet_class(pool_meta, context)
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.sheets.pool import PoolSchema
        from adhocracy_core.sheets.pool import PoolSheet
        from zope.interface.verify import verifyObject
        assert isinstance(inst, PoolSheet)
        assert verifyObject(IResourceSheet, inst)
        assert IResourceSheet.providedBy(inst)
        assert inst.meta.schema_class == PoolSchema
        assert inst.meta.isheet == IPool
        assert inst.meta.editable is False
        assert inst.meta.creatable is False

    def test_get(self, inst,  filter_elements_kwargs,  filter_elements_result):
        appstruct = inst.get()
        assert inst._filter_elements.call_args[1] == filter_elements_kwargs
        assert appstruct == {'elements': filter_elements_result.elements}

    def test_get_depth(self, inst, filter_elements_kwargs):
        inst.get({'depth': '3', 'content_type': 'BlahType', 'count': True})
        filter_elements_kwargs['depth'] = 3
        filter_elements_kwargs['ifaces'] = ['BlahType']
        assert inst._filter_elements.call_args[1] == filter_elements_kwargs

    def test_get_with_two_ifaces_and_two_arbitraryfilters(self, inst,
                                                          filter_elements_kwargs):
        inst.get({'content_type': 'BlahType', 'sheet': 'BlubSheet',
                  'tag': 'BEST', 'rating': 'outstanding'})
        filter_elements_kwargs['arbitrary_filters'] = {'tag': 'BEST',
                                                       'rating': 'outstanding'}
        filter_elements_kwargs['ifaces'] = ['BlahType', 'BlubSheet']
        assert inst._filter_elements.call_args[1] == filter_elements_kwargs

    def test_get_with_depth_all(self, inst, filter_elements_kwargs):
        inst.get({'depth': 'all'})
        filter_elements_kwargs['depth'] = None
        assert inst._filter_elements.call_args[1] == filter_elements_kwargs

    def test_get_with_limit(self, inst, filter_elements_kwargs):
        inst.get({'limit': 2})
        filter_elements_kwargs['limit'] = 2
        assert inst._filter_elements.call_args[1] == filter_elements_kwargs

    def test_get_with_only_visible(self, inst, filter_elements_kwargs):
        inst.get({'only_visible': False})
        filter_elements_kwargs['only_visible'] = False
        assert inst._filter_elements.call_args[1] == filter_elements_kwargs

    def test_get_with_elements_omit(self, inst):
        appstruct = inst.get({'elements': 'omit'})
        assert inst._filter_elements.call_args[1]['resolve_resources'] is False
        assert appstruct == {'elements': []}

    def test_get_with_aggregateby(self, inst, filter_elements_kwargs):
        appstruct = inst.get({'aggregateby': 'interfaces'})
        filter_elements_kwargs['aggregate_filter'] = 'interfaces'
        assert inst._filter_elements.call_args[1] == filter_elements_kwargs
        assert appstruct == {'elements': ['Dummy'], 'aggregateby': {}}

    def test_get_with_aggregateby_elements(self, inst, filter_elements_kwargs):
        inst.get({'aggregateby_elements': 'content'})
        filter_elements_kwargs['aggregate_form'] = 'content'
        assert inst._filter_elements.call_args[1] == filter_elements_kwargs

    def test_get_with_arbitrary_filters(self, inst):
        """remove all standard  and reference filter in get pool requests."""
        from adhocracy_core.rest.schemas import GETPoolRequestSchema
        filters = GETPoolRequestSchema().serialize({})
        arbitrary_filters = {'index1': None}
        filters.update(arbitrary_filters)
        assert inst._get_arbitrary_filters(filters) == arbitrary_filters

    def test_get_reference_filters(self, inst):
        """remove all standard  and arbitrary filter in get pool requests."""
        from adhocracy_core.rest.schemas import GETPoolRequestSchema
        filters = GETPoolRequestSchema().serialize({})
        reference_filters = {'sheet.ISheet1.reference:field1': None}
        filters.update(reference_filters)
        assert inst._get_reference_filters(filters) == reference_filters

    def test_get_cstruct_with_params_content(self, inst, request):
        inst.get = Mock()
        child = testing.DummyResource()
        inst.get.return_value = {'elements': [child]}
        cstruct = inst.get_cstruct(request, params={'elements': 'content'})
        assert cstruct['elements'] == \
            [{'content_type': 'adhocracy_core.interfaces.IResource',
              'data': {},
              'path': 'http://example.com/'}]

    def test_get_cstruct_without_params_content(self, inst, request):
        inst.get = Mock()
        child = testing.DummyResource()
        inst.get.return_value = {'elements': [child]}
        cstruct = inst.get_cstruct(request)
        assert cstruct['elements'] == ['http://example.com/']


@mark.usefixtures('integration')
class TestIntegrationPoolSheet:

    def _make_resource(self, registry, parent=None, name='pool',
                       content_type=IBasicPool):
        from adhocracy_core.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': name}}
        return registry.content.create(
            content_type.__identifier__, parent, appstructs)

    def _get_pool_sheet(self, pool):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        return get_sheet(pool, IPool)

    def test_get_empty(self, registry,  pool_graph_catalog):
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        poolsheet = self._get_pool_sheet(pool)
        assert poolsheet.get() == {'elements': []}

    # TODO: add test if the schema has a children named 'elements' with tagged
    # Value 'target_isheet'. This isheet is used to filter return data.

    def test_get_not_empty_with_target_isheet(self, registry,
                                              pool_graph_catalog):
        from adhocracy_core.interfaces import ISheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        poolsheet = self._get_pool_sheet(pool)
        child = self._make_resource(registry, parent=pool, name='child')
        assert ISheet.providedBy(child)  # ISheet is the default element target isheet
        assert poolsheet._reference_nodes['elements'].reftype.getTaggedValue('target_isheet') == ISheet
        assert poolsheet.get() == {'elements': [child]}

    def test_get_not_empty_without_target_isheet(self, registry,
                                                 pool_graph_catalog):
        from adhocracy_core.interfaces import ISheet
        from zope.interface.declarations import noLongerProvides
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        poolsheet = self._get_pool_sheet(pool)
        child = self._make_resource(registry, parent=pool, name='child')
        noLongerProvides(child, ISheet)
        assert poolsheet._reference_nodes['elements'].reftype.getTaggedValue('target_isheet') == ISheet
        assert poolsheet.get() == {'elements': []}

    def test_get_reference_appstruct_without_params(self, registry,
                                                    pool_graph_catalog):
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        poolsheet = self._get_pool_sheet(pool)
        appstruct = poolsheet._get_reference_appstruct()
        assert appstruct == {'elements': []}

    def test_get_reference_appstruct_with_default_params(self, registry,
                                                         pool_graph_catalog):
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        poolsheet = self._get_pool_sheet(pool)
        appstruct = poolsheet._get_reference_appstruct(
            {'depth': '1', 'count': False})
        assert appstruct == {'elements': []}

    def test_filter_elements_no_filters_with_direct_children(
            self, registry, pool_graph_catalog):
        """If no filter is specified, all direct children are returned."""
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        child1 = self._make_resource(registry, parent=pool, name='child1')
        child2 = self._make_resource(registry, parent=pool, name='child2')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements().elements)
        assert result == {child1, child2}

    def test_filter_elements_no_filters_with_grandchildren_depth1(
            self, registry, pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        child = self._make_resource(registry, parent=pool, name='child')
        self._make_resource(registry, parent=child, name='grandchild')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements().elements)
        assert result == {child}

    def test_filter_elements_no_filters_with_grandchildren_depth2(
            self, registry, pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        child = self._make_resource(registry, parent=pool, name='child')
        grandchild = self._make_resource(registry, parent=child,
                                         name='grandchild')
        self._make_resource(registry, parent=grandchild,
                            name='greatgrandchild')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(depth=2).elements)
        assert result == {child, grandchild}

    def test_filter_elements_no_filters_with_grandchildren_unlimited_depth(
            self, registry, pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        child = self._make_resource(registry, parent=pool, name='child')
        grandchild = self._make_resource(registry, parent=child,
                                         name='grandchild')
        greatgrandchild = self._make_resource(registry, parent=grandchild,
                                              name='greatgrandchild')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(depth=None).elements)
        assert result == {child, grandchild, greatgrandchild}

    def test_filter_elements_only_visible(self, registry, pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        child1 = self._make_resource(registry, parent=pool, name='child1')
        child1.hidden = True
        index = pool_graph_catalog['catalogs']['adhocracy']['private_visibility']
        index.reindex_resource(child1)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(only_visible=True).elements)
        assert result == set()

    def test_filter_elements_by_interface(
            self, registry, pool_graph_catalog):
        from adhocracy_core.interfaces import ITag
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        self._make_resource(registry, parent=pool, name='wrong_type_child')
        right_type_child = self._make_resource(registry, parent=pool,
                                               name='right_type_child',
                                               content_type=ITag)
        self._make_resource(registry, parent=pool_graph_catalog,
                            name='nonchild', content_type=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(ifaces=[ITag]).elements)
        assert result == {right_type_child}

    def test_filter_elements_by_interface_elements_omit(
            self, registry, pool_graph_catalog):
        from adhocracy_core.interfaces import ITag
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        self._make_resource(registry, parent=pool, name='wrong_type_child')
        right_type_child = self._make_resource(registry, parent=pool,
                                               name='right_type_child',
                                               content_type=ITag)
        self._make_resource(registry, parent=pool_graph_catalog,
                            name='nonchild', content_type=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(resolve_resources=False,
                                                ifaces=[ITag]).elements)
        assert result == {right_type_child.__oid__}

    def test_filter_elements_by_two_interfaces_both_present(
            self, registry, pool_graph_catalog):
        from adhocracy_core.interfaces import ITag
        from adhocracy_core.sheets.name import IName
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        self._make_resource(registry, parent=pool, name='wrong_type_child')
        right_type_child = self._make_resource(registry, parent=pool,
                                               name='right_type_child',
                                               content_type=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(ifaces=[ITag, IName]).elements)
        assert result == {right_type_child}

    def test_filter_elements_by_two_interfaces_just_one_present(
            self, registry, pool_graph_catalog):
        from adhocracy_core.interfaces import IItemVersion
        from adhocracy_core.interfaces import ITag
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        self._make_resource(registry, parent=pool, name='child1')
        self._make_resource(registry, parent=pool, name='child2', content_type=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(ifaces=[ITag, IItemVersion]).elements)
        assert result == set()

    def test_filter_elements_by_arbitraryfilter(
            self, registry, pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        untagged_child = self._make_resource(registry, parent=pool,
                                             name='untagged_child')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(arbitrary_filters={'tag': 'LAST'}).elements)
        assert result == set()

    def test_filter_elements_by_referencefilter(self, registry, pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.interfaces import ITag
        from adhocracy_core.sheets import tags
        from adhocracy_core.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        other_child = self._make_resource(registry, parent=pool,
                                          name='other_child')
        tag_child = self._make_resource(registry, parent=pool, content_type=ITag,
                                        name='tag_child')
        tagsheet = get_sheet(tag_child, tags.ITag)
        tagsheet.set({'elements': [pool]})
        poolsheet = get_sheet(pool, IPool)
        reference_filters = {tags.ITag.__identifier__ + ':' + 'elements': pool}
        result = set(poolsheet._filter_elements(references=reference_filters).elements)
        assert result == set([tag_child])

    def test_filter_elements_with_aggregate_filter(self, registry, pool_graph_catalog):
        from adhocracy_core.resources.item import IItem
        from adhocracy_core.resources.itemversion import IItemVersion
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        item = self._make_resource(registry, parent=pool_graph_catalog,
                                   content_type=IItem)
        poolsheet = get_sheet(item, IPool)
        result = poolsheet._filter_elements(aggregate_filter='interfaces').aggregateby
        assert result['interfaces'][str(IItemVersion)] == 1
        # Values not matched by the query shouldn't be reported in the
        # aggregate
        assert str(IItem) not in result['interfaces']

    def test_filter_elements_with_aggregate_form_content(self, registry,
                                                         pool_graph_catalog):
        from adhocracy_core.resources.item import IItem
        from adhocracy_core.resources.itemversion import IItemVersion
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        item = self._make_resource(registry, parent=pool_graph_catalog,
                                   content_type=IItem)
        poolsheet = get_sheet(item, IPool)
        result = poolsheet._filter_elements(aggregate_filter='interfaces',
                                            aggregate_form='content').aggregateby
        itemversion = item['VERSION_0000000']
        assert result['interfaces'][str(IItemVersion)] == [itemversion]

    def test_filter_elements_with_sort_filter(self, registry, pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        item = self._make_resource(registry, parent=pool_graph_catalog,
                                   name='item')
        self._make_resource(registry, parent=item, name='child2')
        self._make_resource(registry, parent=item, name='child1')
        poolsheet = get_sheet(item, IPool)
        result = poolsheet._filter_elements(sort_filter='name').elements
        assert [x.__name__ for x in result] == ['child1', 'child2']

    def test_filter_elements_with_sort_filter_non_sortable(self, registry, pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        item = self._make_resource(registry, parent=pool_graph_catalog,
                                   name='item')
        poolsheet = get_sheet(item, IPool)
        with raises(AssertionError):
            poolsheet._filter_elements(sort_filter='path').elements

    def test_filter_elements_with_limit(self, registry, pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        parentitem = self._make_resource(registry, parent=pool_graph_catalog,
                                         name='parentitem')
        items = [self._make_resource(registry,
                                     parent=parentitem,
                                     name='item{}'.format(i))
                 for i in range(97)]
        poolsheet = get_sheet(parentitem, IPool)
        limit = 17
        result = poolsheet._filter_elements(limit=limit).elements
        assert [x.__name__ for x in result] == \
            [item.__name__ for item in items][:limit]

    def test_filter_elements_with_limit_and_offset(self,
                                                   registry,
                                                   pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        parentitem = self._make_resource(registry, parent=pool_graph_catalog,
                                         name='parentitem')
        nb_items = 23
        items = [self._make_resource(registry,
                                     parent=parentitem,
                                     name='item{}'.format(i))
                 for i in range(nb_items)]
        poolsheet = get_sheet(parentitem, IPool)

        def assert_properties(offset, limit):
            result = poolsheet._filter_elements(limit=limit,
                                                offset=offset).elements
            assert [x.__name__ for x in result] == \
                [item.__name__ for item in items][offset:offset+limit]

        assert_properties(17, 3)

        for (offset, limit) in itertools.product(range(nb_items),
                                                 range(nb_items)):
            assert_properties(offset, limit)

    def test_filter_elements_with_limit_and_offset_notenough_elements(
            self,
            registry,
            pool_graph_catalog):
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.utils import get_sheet
        parentitem = self._make_resource(registry, parent=pool_graph_catalog,
                                         name='parentitem')
        items = [self._make_resource(registry,
                                     parent=parentitem,
                                     name='item{}'.format(i))
                 for i in range(97)]
        poolsheet = get_sheet(parentitem, IPool)
        limit = 20
        offset = 90
        result = poolsheet._filter_elements(limit=limit,
                                            offset=offset).elements
        assert [x.__name__ for x in result] == \
            [item.__name__ for item in items][offset:offset+limit]


@mark.usefixtures('integration')
def test_includeme_register_pool_sheet(config):
    from adhocracy_core.sheets.pool import IPool
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IPool)
    assert get_sheet(context, IPool)
