from pyramid import testing
from pytest import fixture
from pytest import mark


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


@fixture
def mock_sheet(context, mock_sheet, registry):
    from adhocracy.testing import add_and_register_sheet
    from .rate import IRate
    mock_sheet.meta = mock_sheet.meta._replace(isheet=IRate)
    add_and_register_sheet(context, mock_sheet, registry)
    return mock_sheet


def test_index_subscriber(context, mock_sheet):
    from .rate import index_subject
    context['referenced'] = testing.DummyResource()
    mock_sheet.get.return_value = {'subject': context['referenced']}
    assert index_subject(context, None) == '/referenced'


def test_index_object(context, mock_sheet):
    from .rate import index_object
    context['referenced'] = testing.DummyResource()
    mock_sheet.get.return_value = {'object': context['referenced']}
    assert index_object(context, None) == '/referenced'


@fixture
def integration(config):
    config.include('adhocracy.catalog')
    config.include('adhocracy.sheets.rate')


@mark.usefixtures('integration')
def test_includeme_register_rate_sheet(config):
    from adhocracy.sheets.rate import IRate
    from adhocracy.utils import get_sheet
    context = testing.DummyResource(__provides__=IRate)
    inst = get_sheet(context, IRate)
    assert inst.meta.isheet is IRate


@mark.usefixtures('integration')
def test_includeme_register_index_subscriber(registry):
    from .rate import IRate
    from substanced.interfaces import IIndexView
    assert registry.adapters.lookup((IRate,), IIndexView, name='adhocracy|subject')


@mark.usefixtures('integration')
def test_includeme_register_index_subscriber(registry):
    from .rate import IRate
    from substanced.interfaces import IIndexView
    assert registry.adapters.lookup((IRate,), IIndexView, name='adhocracy|object')
