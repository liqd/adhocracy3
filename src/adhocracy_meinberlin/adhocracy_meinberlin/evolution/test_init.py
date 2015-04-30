from pytest import mark
from pytest import fixture


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.organisation')
    config.include('adhocracy_core.resources.asset')
    config.include('adhocracy_core.resources.process')
    config.include('adhocracy_meinberlin.resources.kiezkassen')
    config.include('adhocracy_meinberlin.workflows.kiezkassen')


@mark.usefixtures('integration')
def test_add_sample_organisation(registry, pool):
    from . import add_sample_organisation
    pool = pool
    add_sample_organisation(pool)
    assert pool['organisation']
    assert pool['organisation']['kiezkasse']



