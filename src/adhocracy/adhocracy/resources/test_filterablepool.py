from zope.interface import implementer
from pyramid import testing
from pytest import fixture
from pytest import mark

from adhocracy.interfaces import IResource


@fixture
def integration(config):
    config.include('adhocracy.registry')
    config.include('adhocracy.events')
    config.include('adhocracy.catalog')
    config.include('adhocracy.graph')
    config.include('adhocracy.resources.filterablepool')
    config.include('adhocracy.resources.root')
    config.include('adhocracy.resources.pool')
    config.include('adhocracy.resources.principal')
    config.include('adhocracy.sheets')


class TestFilterablePool:

    def test_create(self, config):
        from adhocracy.resources.filterablepool import FilterablePool
        from adhocracy.interfaces import IFilterablePool
        from zope.interface.verify import verifyObject
        inst = FilterablePool()
        assert IFilterablePool.providedBy(inst)
        assert verifyObject(IFilterablePool, inst)


class TestIntegrationFilterablePool:

    @fixture(scope='function')
    def root(self, config):
        import logging
        logging.warning('root created')
        from adhocracy.resources.root import IRootPool
        return config.registry.content.create(IRootPool.__identifier__)

    def _make_one(self, config, parent=None, name='inst'):
        from adhocracy.resources.filterablepool import IBasicFilterablePool
        from adhocracy.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': name}}
        return config.registry.content.create(
            IBasicFilterablePool.__identifier__, parent, appstructs)

    @mark.usefixtures('integration')
    def test_includeme_registry_register_factories(self, config):
        from adhocracy.resources.filterablepool import IBasicFilterablePool
        content_types = config.registry.content.factory_types
        assert IBasicFilterablePool.__identifier__ in content_types

    @mark.usefixtures('integration')
    def test_includeme_registry_register_meta(self, config):
        from adhocracy.resources.filterablepool import IBasicFilterablePool
        meta = config.registry.content.meta
        assert IBasicFilterablePool.__identifier__ in meta

    @mark.usefixtures('integration')
    def test_includeme_registry_create_content(self, config):
        from adhocracy.resources.filterablepool import IBasicFilterablePool
        assert config.registry.content.create(
            IBasicFilterablePool.__identifier__)

    @mark.usefixtures('integration')
    def test_filtered_elements_no_filters(self, config, root):
        """If no filter is specified, all direct children are returned."""
        inst = self._make_one(config, root)
        child1 = testing.DummyResource()
        child2 = testing.DummyResource()
        inst.add('child1', child1)
        inst.add('child2', child2)
        result = list(inst.filtered_elements())
        assert len(result) == 2
        assert child1 in result
        assert child2 in result

    @mark.usefixtures('integration')
    def test_filtered_elements_no_grandchildren(self, config, root):
        """No children of children are returned."""
        from adhocracy.resources.pool import Pool
        inst = self._make_one(config, root)
        child_pool = Pool()
        inst.add('child', child_pool)
        grandchild = testing.DummyResource()
        child_pool.add('child', grandchild)
        result = list(inst.filtered_elements())
        assert len(result) == 1
        assert grandchild not in result

    @mark.usefixtures('integration')
    def test_filtered_elements_interface_filter(self, config, root):
        from adhocracy.interfaces import IItemVersion
        inst = self._make_one(config, root)
        version_child = testing.DummyResource(__provides__=IItemVersion)
        from substanced.util import get_interfaces
        ifaces = get_interfaces(version_child, classes=False)
        assert IItemVersion in ifaces
        other_child = testing.DummyResource()
        inst.add('child1', version_child)
        inst.add('child2', other_child)
        from zope.interface import Interface
        result = list(inst.interface_filter(Interface))
        # TODO there are all the other objects?
        assert len(result) == 1
        from substanced.util import find_catalog
        catalog = find_catalog(inst, 'system')
        assert catalog in result
