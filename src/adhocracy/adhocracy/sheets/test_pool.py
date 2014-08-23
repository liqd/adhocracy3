from pyramid import testing
from pytest import fixture


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
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}

    #FIXME: add check if the schema has a children named 'elements' with tagged
    #Value 'target_isheet'. This isheet is used to filter return data.

    def test_get_not_empty_with_target_isheet(self, meta, context):
        from adhocracy.interfaces import ISheet
        child = testing.DummyResource(__provides__=ISheet)
        context['child1'] = child
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': [child]}

    def test_get_not_empty_without_target_isheet(self, meta, context):
        child = testing.DummyResource()
        context['child1'] = child
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}


def test_includeme_register_pool_sheet(config):
    from adhocracy.sheets.pool import IPool
    from adhocracy.utils import get_sheet
    config.include('adhocracy.sheets.pool')
    context = testing.DummyResource(__provides__=IPool)
    assert get_sheet(context, IPool)
