from pytest import fixture
from pytest import mark


@fixture
def integration(config, pool_graph_catalog):
    config.include('pyramid_mailer.testing')
    config.include('adhocracy_spd')


def test_root_meta():
    from adhocracy_core.resources.root import root_meta
    from adhocracy_core.resources.root import \
        create_initial_content_for_app_root
    from .root import add_spd_process
    from .root import spd_root_meta
    assert add_spd_process not in root_meta.after_creation
    assert add_spd_process in spd_root_meta.after_creation
    assert create_initial_content_for_app_root in\
           spd_root_meta.after_creation


@mark.usefixtures('integration')
def test_add_spd_process(pool, registry):
    from .digital_leben import IProcess
    from .root import add_spd_process
    add_spd_process(pool, registry, {})
    IProcess.providedBy(pool['digital_leben'])

