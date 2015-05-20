from pytest import mark
from pytest import fixture


@fixture
def integration(config):
    config.include('adhocracy_meinberlin')
