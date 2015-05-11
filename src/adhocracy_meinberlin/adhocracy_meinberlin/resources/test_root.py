from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_meinberlin')


def test_root_meta():
    from adhocracy_core.resources.root import root_meta
    from adhocracy_core.resources.root import \
        create_initial_content_for_app_root
    from .root import create_initial_content_for_meinberlin
    from .root import meinberlin_root_meta
    assert create_initial_content_for_meinberlin not in root_meta.after_creation
    assert create_initial_content_for_meinberlin in\
           meinberlin_root_meta.after_creation
    assert create_initial_content_for_app_root in\
           meinberlin_root_meta.after_creation


@mark.usefixtures('integration')
def test_create_initial_content_for_meinberlin(pool, registry):
    from adhocracy_core.resources.organisation import IOrganisation
    from .root import IProcess
    from .root import create_initial_content_for_meinberlin
    create_initial_content_for_meinberlin(pool, registry, {})
    assert IOrganisation.providedBy(pool['organisation'])
    assert IProcess.providedBy(pool['organisation']['kiezkasse'])



