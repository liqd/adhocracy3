from pytest import fixture
from pytest import mark


@fixture
def integration(config, pool_graph_catalog):
    config.include('adhocracy_mercator')


def test_root_meta():
    from adhocracy_core.resources.root import root_meta
    from adhocracy_core.resources.root import \
        create_initial_content_for_app_root
    from .root import add_mercator_process
    from .root import mercator_root_meta
    assert add_mercator_process not in root_meta.after_creation
    assert add_mercator_process in mercator_root_meta.after_creation
    assert create_initial_content_for_app_root in \
        mercator_root_meta.after_creation


@mark.usefixtures('integration')
def test_create_root_with_initial_content(registry):
        from adhocracy_core.resources.root import IRootPool
        from adhocracy_core.resources.organisation import IOrganisation
        from adhocracy_core.resources.process import IProcess
        inst = registry.content.create(IRootPool.__identifier__)
        assert IRootPool.providedBy(inst)
        assert IOrganisation.providedBy(inst['mercator'])
        assert IProcess.providedBy(inst['mercator']['advocate'])

