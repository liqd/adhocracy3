from pyramid import testing
from pytest import fixture


class TestRateSheet:

    @fixture
    def meta(self):
        from adhocracy.sheets.rate import rate_meta
        return rate_meta

    def test_create(self, meta, context):
        from adhocracy.sheets.rate import IRate
        from adhocracy.sheets.rate import RateSchema
        from adhocracy.sheets import GenericResourceSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, GenericResourceSheet)
        assert inst.meta.isheet == IRate
        assert inst.meta.schema_class == RateSchema
        assert inst.meta.create_mandatory

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'subject': '',
                              'object': '',
                              'rate': 0,
                              }


def test_includeme_register_rate_sheet(config):
    from adhocracy.sheets.rate import IRate
    from adhocracy.utils import get_sheet
    config.include('adhocracy.sheets.rate')
    context = testing.DummyResource(__provides__=IRate)
    inst = get_sheet(context, IRate)
    assert inst.meta.isheet is IRate
