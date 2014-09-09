from pytest import fixture
from pytest import mark

from adhocracy.resources.filterablepool import IBasicFilterablePool


@fixture
def integration(config):
    config.include('adhocracy.events')
    config.include('adhocracy.registry')
    config.include('adhocracy.resources.filterablepool')
    config.include('adhocracy.resources.tag')
    config.include('adhocracy.sheets')


class TestFilterablePool:

    def test_create(self):
        from adhocracy.resources.filterablepool import FilterablePool
        from adhocracy.interfaces import IFilterablePool
        from zope.interface.verify import verifyObject
        inst = FilterablePool()
        assert IFilterablePool.providedBy(inst)
        assert verifyObject(IFilterablePool, inst)


@mark.usefixtures('integration')
class TestIntegrationFilterablePool:

    def _make_one(self, registry, parent=None, name='inst',
                  restype=IBasicFilterablePool):
        from adhocracy.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': name}}
        return registry.content.create(
            restype.__identifier__, parent, appstructs)

    def test_includeme_registry_register_factories(self, registry):
        from adhocracy.resources.filterablepool import IBasicFilterablePool
        content_types = registry.content.factory_types
        assert IBasicFilterablePool.__identifier__ in content_types

    def test_includeme_registry_register_meta(self, registry):
        from adhocracy.resources.filterablepool import IBasicFilterablePool
        meta = registry.content.meta
        assert IBasicFilterablePool.__identifier__ in meta

    def test_includeme_registry_create_content(self, registry):
        from adhocracy.resources.filterablepool import IBasicFilterablePool
        assert registry.content.create(IBasicFilterablePool.__identifier__)

    def test_filtered_elements_no_filters_with_direct_children(
            self, registry, pool_graph_catalog):
        """If no filter is specified, all direct children are returned."""
        inst = self._make_one(registry, parent=pool_graph_catalog)
        child1 = self._make_one(registry, parent=inst, name='child1')
        child2 = self._make_one(registry, parent=inst, name='child2')
        result = set(inst.filtered_elements())
        assert result == {child1, child2}

    def test_filtered_elements_no_filters_with_grandchildren_depth1(
            self, registry, pool_graph_catalog):
        inst = self._make_one(registry, parent=pool_graph_catalog)
        child = self._make_one(registry, parent=inst, name='child')
        self._make_one(registry, parent=child, name='grandchild')
        result = set(inst.filtered_elements())
        assert result == {child}

    def test_filtered_elements_no_filters_with_grandchildren_depth2(
            self, registry, pool_graph_catalog):
        inst = self._make_one(registry, parent=pool_graph_catalog)
        child = self._make_one(registry, parent=inst, name='child')
        grandchild = self._make_one(registry, parent=child, name='grandchild')
        self._make_one(registry, parent=grandchild,  name='greatgrandchild')
        result = set(inst.filtered_elements(depth=2))
        assert result == {child, grandchild}

    def test_filtered_elements_no_filters_with_grandchildren_unlimited_depth(
            self, registry, pool_graph_catalog):
        inst = self._make_one(registry, parent=pool_graph_catalog)
        child = self._make_one(registry, parent=inst, name='child')
        grandchild = self._make_one(registry, parent=child, name='grandchild')
        greatgrandchild = self._make_one(registry, parent=grandchild,
                                         name='greatgrandchild')
        result = set(inst.filtered_elements(depth=None))
        assert result == {child, grandchild, greatgrandchild}

    def test_filtered_elements_by_interface(
            self, registry, pool_graph_catalog):
        from adhocracy.interfaces import ITag
        inst = self._make_one(registry, parent=pool_graph_catalog)
        self._make_one(registry, parent=inst, name='wrong_type_child')
        right_type_child = self._make_one(registry, parent=inst,
                                          name='right_type_child',
                                          restype=ITag)
        self._make_one(registry, parent=pool_graph_catalog, name='nonchild',
                       restype=ITag)
        result = set(inst.filtered_elements(ifaces=[ITag]))
        assert result == {right_type_child}

    def test_filtered_elements_by_two_interfaces_both_present(
            self, registry, pool_graph_catalog):
        from adhocracy.interfaces import ITag
        from adhocracy.sheets.name import IName
        inst = self._make_one(registry, parent=pool_graph_catalog)
        self._make_one(registry, parent=inst, name='wrong_type_child')
        right_type_child = self._make_one(registry, parent=inst,
                                          name='right_type_child',
                                          restype=ITag)
        result = set(inst.filtered_elements(ifaces=[ITag, IName]))
        assert result == {right_type_child}

    def test_filtered_elements_by_two_interfaces_just_one_present(
            self, registry, pool_graph_catalog):
        from adhocracy.interfaces import IItemVersion
        from adhocracy.interfaces import ITag
        inst = self._make_one(registry, parent=pool_graph_catalog)
        self._make_one(registry, parent=inst, name='child1')
        self._make_one(registry, parent=inst, name='child2', restype=ITag)
        result = set(inst.filtered_elements(ifaces=[ITag, IItemVersion]))
        assert result == set()
