from pyramid import testing
from pytest import fixture
from pytest import mark

from adhocracy.resources.pool import IBasicPool


@fixture
def integration(config):
    config.include('adhocracy.events')
    config.include('adhocracy.registry')
    config.include('adhocracy.resources.pool')
    config.include('adhocracy.resources.tag')
    config.include('adhocracy.sheets')


class TestPoolSheet:

    @fixture
    def meta(self):
        from adhocracy.sheets.pool import pool_metadata
        return pool_metadata

    def test_create(self, meta, context):
        from adhocracy.interfaces import IResourceSheet
        from adhocracy.sheets.pool import IPool
        from adhocracy.sheets.pool import PoolSchema
        from adhocracy.sheets.pool import PoolSheet
        from zope.interface.verify import verifyObject
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, PoolSheet)
        assert verifyObject(IResourceSheet, inst)
        assert IResourceSheet.providedBy(inst)
        assert inst.meta.schema_class == PoolSchema
        assert inst.meta.isheet == IPool
        assert inst.meta.editable is False
        assert inst.meta.creatable is False

    def test_get_empty(self, meta, context):
        import colander
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': [], 'count': colander.drop}

    #FIXME: add check if the schema has a children named 'elements' with tagged
    #Value 'target_isheet'. This isheet is used to filter return data.

    def test_get_not_empty_with_target_isheet(self, meta, context):
        from adhocracy.interfaces import ISheet
        import colander
        child = testing.DummyResource(__provides__=ISheet)
        context['child1'] = child
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': [child], 'count': colander.drop}

    def test_get_not_empty_without_target_isheet(self, meta, context):
        import colander
        child = testing.DummyResource()
        context['child1'] = child
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': [], 'count': colander.drop}


@mark.usefixtures('integration')
class TestIntegrationPoolSheet:

    def _make_resource(self, registry, parent=None, name='pool',
                  restype=IBasicPool):
        from adhocracy.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': name}}
        return registry.content.create(
            restype.__identifier__, parent, appstructs)

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
                                               restype=ITag)
        self._make_resource(registry, parent=pool_graph_catalog,
                            name='nonchild', restype=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(ifaces=[ITag]))
        assert result == {right_type_child}

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
                                               restype=ITag)
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
        self._make_resource(registry, parent=pool, name='child2', restype=ITag)
        poolsheet = get_sheet(pool, IPool)
        result = set(poolsheet._filter_elements(ifaces=[ITag, IItemVersion]))
        assert result == set()


def test_includeme_register_pool_sheet(config):
    from adhocracy.sheets.pool import IPool
    from adhocracy.utils import get_sheet
    config.include('adhocracy.sheets.pool')
    context = testing.DummyResource(__provides__=IPool)
    assert get_sheet(context, IPool)
