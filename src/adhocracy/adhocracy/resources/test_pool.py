import unittest

from pyramid import testing


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.testing import create_folder_with_graph
        config = testing.setUp()
        config.include('adhocracy.registry')
        config.include('adhocracy.events')
        config.include('adhocracy.sheets.metadata')
        config.include('adhocracy.resources.pool')
        self.config = config
        self.context = create_folder_with_graph()

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        from adhocracy.resources.pool import IBasicPool
        content_types = self.config.registry.content.factory_types
        assert IBasicPool.__identifier__ in content_types

    def test_includeme_registry_register_meta(self):
        from adhocracy.resources.pool import IBasicPool
        from adhocracy.resources.pool import pool_metadata
        meta = self.config.registry.content.meta
        assert IBasicPool.__identifier__ in meta
        assert meta[IBasicPool.__identifier__]['resource_metadata'] == pool_metadata


    def test_includeme_registry_create_content(self):
        from adhocracy.resources.pool import IBasicPool
        res = self.config.registry.content.create(IBasicPool.__identifier__)
        assert IBasicPool.providedBy(res)


class PoolUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, d=None):
        from adhocracy.resources.pool import Pool
        return Pool(d)

    def test_create(self):
        from adhocracy.interfaces import IPool
        from zope.interface.verify import verifyObject
        inst = self._makeOne()
        assert verifyObject(IPool, inst)

    def test_next_name_empty(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        assert inst.next_name(ob) == '0'.zfill(7)
        assert inst.next_name(ob) == '1'.zfill(7)

    def test_next_name_nonempty(self):
        ob = testing.DummyResource()
        inst = self._makeOne({'nonintifiable': ob})
        assert inst.next_name(ob) == '0'.zfill(7)

    def test_next_name_nonempty_intifiable(self):
        ob = testing.DummyResource()
        inst = self._makeOne({'0000000': ob})
        assert inst.next_name(ob).startswith('0'.zfill(7) + '_20')

    def test_next_name_empty_prefix(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        assert inst.next_name(ob, prefix='prefix') == 'prefix' + '0'.zfill(7)
        assert inst.next_name(ob,) == '1'.zfill(7)

    def test_add(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        inst.add('name', ob)
        assert 'name' in inst

    def test_add_next(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        inst.add_next(ob)
        assert '0'.zfill(7) in inst

    def test_add_next_prefix(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        inst.add_next(ob, prefix='prefix')
        assert 'prefix' + '0'.zfill(7) in inst
