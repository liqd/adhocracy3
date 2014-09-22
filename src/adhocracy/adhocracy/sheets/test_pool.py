from pyramid import testing
from pytest import fixture
from pytest import mark
from unittest.mock import Mock

from adhocracy.resources.pool import IBasicPool


@fixture
def integration(config):
    config.include('adhocracy.events')
    config.include('adhocracy.registry')
    config.include('adhocracy.catalog')
    config.include('adhocracy.resources.pool')
    config.include('adhocracy.resources.tag')
    config.include('adhocracy.sheets')


class TestFilteringPoolSheet:

    @fixture
    def meta(self):
        from adhocracy.sheets.pool import pool_metadata
        return pool_metadata

    @fixture
    def inst(self, meta, context):
        inst = meta.sheet_class(meta, context)
        inst._filter_elements = Mock(spec=inst._filter_elements)
        inst._filter_elements.return_value = []
        return inst

    def test_create(self, inst):
        from adhocracy.interfaces import IResourceSheet
        from adhocracy.sheets.pool import IPool
        from adhocracy.sheets.pool import PoolSchema
        from adhocracy.sheets.pool import PoolSheet
        from zope.interface.verify import verifyObject
        assert isinstance(inst, PoolSheet)
        assert verifyObject(IResourceSheet, inst)
        assert IResourceSheet.providedBy(inst)
        assert inst.meta.schema_class == PoolSchema
        assert inst.meta.isheet == IPool
        assert inst.meta.editable is False
        assert inst.meta.creatable is False

    def test_get_empty(self, inst):
        import colander
        assert inst.get() == {'elements': [], 'count': colander.drop}

    #FIXME: add check if the schema has a children named 'elements' with tagged
    #Value 'target_isheet'. This isheet is used to filter return data.

    def test_get_not_empty_with_target_isheet(self, inst, context):
        from adhocracy.interfaces import ISheet
        import colander
        child = testing.DummyResource(__provides__=ISheet)
        context['child1'] = child
        assert inst.get() == {'elements': [child], 'count': colander.drop}

    def test_get_not_empty_without_target_isheet(self, inst, context):
        import colander
        child = testing.DummyResource()
        context['child1'] = child
        assert inst.get() == {'elements': [], 'count': colander.drop}

    def test_get_reference_appstruct_without_params(self, inst):
        appstruct = inst._get_reference_appstruct()
        assert inst._filter_elements.called is False
        assert appstruct == {'elements': []}

    def test_get_reference_appstruct_with_depth(self, inst):
        inst._filter_elements.return_value = ['Dummy']
        appstruct = inst._get_reference_appstruct(
            {'depth': '3', 'content_type': 'BlahType', 'count': True})
        assert inst._filter_elements.call_args[1] == {'depth': 3,
                                                      'ifaces': ['BlahType'],
                                                      'arbitrary_filters': {},
                                                      'resolve_resources': True,
                                                      'references': {},
                                                      }
        assert appstruct == {'elements': ['Dummy'], 'count': 1}

    def test_get_reference_appstruct_with_two_ifaces_and_two_arbitraryfilters(self, inst):
        inst._filter_elements.return_value = ['Dummy']
        appstruct = inst._get_reference_appstruct(
            {'content_type': 'BlahType', 'sheet': 'BlubSheet',
             'tag': 'BEST', 'rating': 'outstanding'})
        assert inst._filter_elements.call_args[1] == {
            'depth': 1,
            'ifaces': ['BlahType', 'BlubSheet'],
            'arbitrary_filters': {'tag': 'BEST', 'rating': 'outstanding'},
            'resolve_resources': True,
            'references': {},
            }
        assert appstruct == {'elements': ['Dummy']}

    def test_get_reference_appstruct_with_default_params(self, inst):
        appstruct = inst._get_reference_appstruct(
            {'depth': '1', 'count': False})
        assert inst._filter_elements.called is False
        assert appstruct == {'elements': []}

    def test_get_reference_appstruct_with_depth_all(self, inst):
        inst._filter_elements.return_value = ['Dummy']
        appstruct = inst._get_reference_appstruct({'depth': 'all'})
        assert inst._filter_elements.call_args[1] == \
               {'depth': None,
                'ifaces': [],
                'arbitrary_filters': {},
                'resolve_resources': True,
                'references': {},
                }
        assert appstruct == {'elements': ['Dummy']}

    def test_get_reference_appstruct_with_elements_omit(self, inst):
        inst._filter_elements.return_value = ['Dummy']
        appstruct = inst._get_reference_appstruct({'elements': 'omit'})
        assert inst._filter_elements.call_args[1]['resolve_resources'] is False
        assert 'elements' not in appstruct

    def test_get_arbitrary_filters(self, meta, context):
        """remove all standard  and reference filter in get pool requests."""
        from adhocracy.rest.schemas import GETPoolRequestSchema
        inst = meta.sheet_class(meta, context)
        filters = GETPoolRequestSchema().serialize({})
        arbitrary_filters = {'index1': None}
        filters.update(arbitrary_filters)
        assert inst._get_arbitrary_filters(filters) == arbitrary_filters

    def test_get_reference_filters(self, meta, context):
        """remove all standard  and arbitrary filter in get pool requests."""
        from adhocracy.rest.schemas import GETPoolRequestSchema
        inst = meta.sheet_class(meta, context)
        filters = GETPoolRequestSchema().serialize({})
        reference_filters = {'sheet.ISheet1.reference:field1': None}
        filters.update(reference_filters)
        assert inst._get_reference_filters(filters) == reference_filters


@mark.usefixtures('integration')
class TestIntegrationPoolSheet:

    def _make_resource(self, registry, parent=None, name='pool',
                       content_type=IBasicPool):
        from adhocracy.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': name}}
        return registry.content.create(
            content_type.__identifier__, parent, appstructs)

    def test_filter_elements_no_filters_with_direct_children(
            self, registry, pool_graph_catalog):
        """If no filter is specified, all direct children are returned."""
        from adhocracy.sheets.pool import IPool
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        child1 = self._make_resource(registry, parent=pool, name='child1')
        child2 = self._make_resource(registry, parent=pool, name='child2')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements())
        assert result == {child1, child2}

    def test_filter_elements_no_filters_with_grandchildren_depth1(
            self, registry, pool_graph_catalog):
        from adhocracy.sheets.pool import IPool
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        child = self._make_resource(registry, parent=pool, name='child')
        self._make_resource(registry, parent=child, name='grandchild')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements())
        assert result == {child}

    def test_filter_elements_no_filters_with_grandchildren_depth2(
            self, registry, pool_graph_catalog):
        from adhocracy.sheets.pool import IPool
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        child = self._make_resource(registry, parent=pool, name='child')
        grandchild = self._make_resource(registry, parent=child,
                                         name='grandchild')
        self._make_resource(registry, parent=grandchild,
                            name='greatgrandchild')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(depth=2))
        assert result == {child, grandchild}

    def test_filter_elements_no_filters_with_grandchildren_unlimited_depth(
            self, registry, pool_graph_catalog):
        from adhocracy.sheets.pool import IPool
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        child = self._make_resource(registry, parent=pool, name='child')
        grandchild = self._make_resource(registry, parent=child,
                                         name='grandchild')
        greatgrandchild = self._make_resource(registry, parent=grandchild,
                                              name='greatgrandchild')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(depth=None))
        assert result == {child, grandchild, greatgrandchild}

    def test_filter_elements_by_interface(
            self, registry, pool_graph_catalog):
        from adhocracy.interfaces import ITag
        from adhocracy.sheets.pool import IPool
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        self._make_resource(registry, parent=pool, name='wrong_type_child')
        right_type_child = self._make_resource(registry, parent=pool,
                                               name='right_type_child',
                                               content_type=ITag)
        self._make_resource(registry, parent=pool_graph_catalog,
                            name='nonchild', content_type=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(ifaces=[ITag]))
        assert result == {right_type_child}

    def test_filter_elements_by_interface_elements_omit(
            self, registry, pool_graph_catalog):
        from adhocracy.interfaces import ITag
        from adhocracy.sheets.pool import IPool
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        self._make_resource(registry, parent=pool, name='wrong_type_child')
        right_type_child = self._make_resource(registry, parent=pool,
                                               name='right_type_child',
                                               content_type=ITag)
        self._make_resource(registry, parent=pool_graph_catalog,
                            name='nonchild', content_type=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(resolve_resources=False, ifaces=[ITag]))
        assert result == {right_type_child.__oid__}

    def test_filter_elements_by_two_interfaces_both_present(
            self, registry, pool_graph_catalog):
        from adhocracy.interfaces import ITag
        from adhocracy.sheets.name import IName
        from adhocracy.sheets.pool import IPool
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        self._make_resource(registry, parent=pool, name='wrong_type_child')
        right_type_child = self._make_resource(registry, parent=pool,
                                               name='right_type_child',
                                               content_type=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(ifaces=[ITag, IName]))
        assert result == {right_type_child}

    def test_filter_elements_by_two_interfaces_just_one_present(
            self, registry, pool_graph_catalog):
        from adhocracy.interfaces import IItemVersion
        from adhocracy.interfaces import ITag
        from adhocracy.sheets.pool import IPool
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        self._make_resource(registry, parent=pool, name='child1')
        self._make_resource(registry, parent=pool, name='child2', content_type=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(ifaces=[ITag, IItemVersion]))
        assert result == set()

    def test_filter_elements_by_arbitraryfilter(
            self, registry, pool_graph_catalog):
        from adhocracy.sheets.pool import IPool
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        untagged_child = self._make_resource(registry, parent=pool,
                                             name='untagged_child')
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(arbitrary_filters={'tag': 'LAST'}))
        assert result == set()

    def test_filter_elements_by_referencefilter(self, registry, pool_graph_catalog):
        from adhocracy.sheets.pool import IPool
        from adhocracy.interfaces import ITag
        from adhocracy.sheets import tags
        from adhocracy.utils import get_sheet
        pool = self._make_resource(registry, parent=pool_graph_catalog)
        other_child = self._make_resource(registry, parent=pool,
                                          name='other_child')
        tag_child = self._make_resource(registry, parent=pool, content_type=ITag,
                                        name='tag_child')
        tagsheet = get_sheet(tag_child, tags.ITag)
        tagsheet.set({'elements': [pool]})
        poolsheet = get_sheet(pool, IPool)
        reference_filters = {tags.ITag.__identifier__ + ':' + 'elements': pool}
        result = set(poolsheet._filter_elements(references=reference_filters))
        assert result == set([tag_child])



@mark.usefixtures('integration')
def test_includeme_register_pool_sheet(config):
    from adhocracy.sheets.pool import IPool
    from adhocracy.utils import get_sheet
    context = testing.DummyResource(__provides__=IPool)
    assert get_sheet(context, IPool)
