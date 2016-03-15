from pytest import fixture
from pytest import mark

from pyramid import testing


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_sample.sheets')


@mark.usefixtures('integration')
def test_create_namedummy_sheet(registry):
    from adhocracy_core.sheets.name import IName
    from adhocracy_sample.sheets.sample_sheets import DummyNameSheet
    context = testing.DummyResource(__provides__=IName)
    inst = registry.content.get_sheet(context, IName)
    assert isinstance(inst, DummyNameSheet)


@mark.usefixtures('integration')
def test_create_extendendname_sheet(registry):
    from adhocracy_sample.sheets.sample_sheets import IExtendedName
    context = testing.DummyResource(__provides__=IExtendedName)
    inst = registry.content.get_sheet(context, IExtendedName)
    appstruct = inst.get()
    assert 'description_x' in appstruct
