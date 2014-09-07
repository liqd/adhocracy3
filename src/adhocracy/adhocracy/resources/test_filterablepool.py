from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy.events')
    config.include('adhocracy.registry')
    config.include('adhocracy.resources.filterablepool')
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

    def _make_one(self, registry, parent=None, name='inst'):
        from adhocracy.resources.filterablepool import IBasicFilterablePool
        from adhocracy.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': name}}
        return registry.content.create(
            IBasicFilterablePool.__identifier__, parent, appstructs)

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

    def test_filtered_elements_no_filters_with_direct_children(self, registry, pool_graph_catalog):
        """If no filter is specified, all direct children are returned."""
        inst = self._make_one(registry, parent=pool_graph_catalog)
        child1 = testing.DummyResource()
        child2 = testing.DummyResource()
        inst['child1'] = child1
        inst['child2'] = child2
        result = list(inst.filtered_elements())
        assert result == [child1, child2]

    def test_filtered_elements_no_filters_with_grandchildren(self, registry, pool_graph_catalog):
        """No children of children are returned."""
        inst = self._make_one(registry, parent=pool_graph_catalog)
        child = testing.DummyResource()
        inst['child'] = child
        grandchild = testing.DummyResource()
        inst['child']['grandchild'] = grandchild
        result = list(inst.filtered_elements())
        assert result == [child]

    def test_filtered_elements_interface_filter(self, registry, pool_graph_catalog):
        from adhocracy.interfaces import IItemVersion
        inst = self._make_one(registry, parent=pool_graph_catalog)
        child1 = testing.DummyResource()
        child2 = testing.DummyResource(__provides__=IItemVersion)
        inst['child1'] = child1
        inst['child2'] = child2
        result = list(inst.interface_filter(IItemVersion))
        assert result == [child2]

        # from substanced.util import get_interfaces
        # inst = self._make_one(registry, parent=pool_graph_catalog)
        # version_child = testing.DummyResource(__provides__=IItemVersion)
        # ifaces = get_interfaces(version_child, classes=False)
        #
        # other_child = testing.DummyResource()
        # inst.add('child1', version_child)
        # inst.add('child2', other_child)
        # from zope.interface import Interface
        # result = list(inst.interface_filter(Interface))
        # # TODO there are all the other objects?
        # assert len(result) == 1
        # from substanced.util import find_catalog
        # catalog = find_catalog(inst, 'system')
        # assert catalog in result
        # assert catalog in result
