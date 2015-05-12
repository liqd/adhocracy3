from pytest import mark
from pytest import fixture


@fixture
def integration(config):
    config.include('adhocracy_meinberlin')


@mark.usefixtures('integration')
def test_add_sample_organisation(registry, pool):
    from . import add_sample_organisation
    add_sample_organisation(pool)
    assert pool['organisation']
    assert pool['organisation']['kiezkasse']



