from pyramid import testing
from pytest import mark
from pytest import fixture


def test_pool_meta():
    from .pool import pool_meta
    from .pool import IPool
    from .pool import Pool
    import adhocracy_core.sheets
    meta = pool_meta
    assert meta.iresource is IPool
    assert meta.content_class is Pool
    assert meta.is_implicit_addable is False
    assert meta.basic_sheets == [adhocracy_core.sheets.name.IName,
                                 adhocracy_core.sheets.title.ITitle,
                                 adhocracy_core.sheets.pool.IPool,
                                 adhocracy_core.sheets.metadata.IMetadata,
                                 ]
    assert meta.element_types == [IPool]
    assert meta.is_implicit_addable is False
    assert meta.permission_create == 'create_pool'


def test_poolbasic_meta():
    from .pool import basicpool_meta
    from .pool import IBasicPool
    meta = basicpool_meta
    assert meta.iresource is IBasicPool
    assert meta.is_implicit_addable


@mark.usefixtures('integration')
class TestPool:

    def test_create_pool(self, registry):
        from adhocracy_core.resources.pool import IBasicPool
        res = registry.content.create(IBasicPool.__identifier__)
        assert IBasicPool.providedBy(res)


class TestPoolClass:

    def _makeOne(self, d=None):
        from adhocracy_core.resources.pool import Pool
        return Pool(d)

    def test_create(self):
        from adhocracy_core.interfaces import IPool
        from zope.interface.verify import verifyObject
        inst = self._makeOne()
        assert verifyObject(IPool, inst)
        assert IPool.providedBy(inst)

    def test_next_name_empty(self, context):
        inst = self._makeOne()
        assert inst.next_name(context) == '0'.zfill(7)
        assert inst.next_name(context) == '1'.zfill(7)

    def test_next_name_nonempty(self, context):
        inst = self._makeOne({'nonintifiable': context})
        assert inst.next_name(context) == '0'.zfill(7)

    def test_next_name_nonempty_intifiable(self, context):
        inst = self._makeOne({'0000000': context})
        assert inst.next_name(context).startswith('0'.zfill(7) + '_20')

    def test_next_name_empty_prefix(self, context):
        inst = self._makeOne()
        assert inst.next_name(context, prefix='prefix')\
            == 'prefix' + '0'.zfill(7)
        assert inst.next_name(context) == '1'.zfill(7)

    def test_add(self, context):
        inst = self._makeOne()
        inst.add('name', context)
        assert 'name' in inst

    def test_add_next(self, context):
        inst = self._makeOne()
        inst.add_next(context)
        assert '0'.zfill(7) in inst

    def test_add_next_prefix(self, context):
        inst = self._makeOne()
        inst.add_next(context, prefix='prefix')
        assert 'prefix' + '0'.zfill(7) in inst

    def test_find_service(self, service):
        inst = self._makeOne()
        inst['service'] = service
        service = inst.find_service('service')
        assert service is inst['service']
