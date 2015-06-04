from pytest import fixture
from pytest import mark
from pyramid import testing
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS

@fixture
def integration(config, pool_graph_catalog):
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.resources.geo')
    config.include('adhocracy_core.resources.asset')
    config.include('adhocracy_core.resources.root')
    config.include('adhocracy_core.resources.pool')
    config.include('adhocracy_core.resources.principal')
    config.include('adhocracy_core.resources.badge')
    config.include('adhocracy_core.rest')
    config.include('adhocracy_core.workflows.sample')
    config.include('adhocracy_core.resources.process')
    config.include('adhocracy_mercator')
    config.include('adhocracy_mercator.workflows')
    config.include('adhocracy_mercator.resources.mercator')


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
    from adhocracy_mercator.resources.mercator import IProcess
    inst = registry.content.create(IRootPool.__identifier__)
    assert IRootPool.providedBy(inst)
    assert IProcess.providedBy(inst['mercator'])


@mark.usefixtures('integration')
def test_initialize_workflow(registry):
    from adhocracy_mercator.resources.root import initialize_workflow
    root = testing.DummyResource()
    mercator = testing.DummyResource()
    root['mercator'] = mercator
    root.__acl__ = [(Allow, 'role:god', ALL_PERMISSIONS)]
    workflow = registry.content.workflows['mercator']
    initialize_workflow(root, registry, {})
    assert workflow.state_of(mercator) == 'participate'
