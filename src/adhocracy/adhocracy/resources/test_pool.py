import unittest

from pyramid import testing


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

    def next_name(self, obj, prefix=''):
        return prefix + '_0000000'


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('substanced.content')
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.pool')
        self.context = DummyFolder()

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