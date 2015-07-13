from pytest import fixture
from pytest import mark
from pyramid import testing
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from unittest.mock import Mock

@fixture
def integration(integration):
    integration.include('pyramid_mailer.testing')
    integration.include('adhocracy_core.workflows')
    integration.include('adhocracy_mercator.workflows')


def test_root_meta():
    from adhocracy_core.resources.root import root_meta
    from adhocracy_core.resources.root import \
        create_initial_content_for_app_root
    from adhocracy_core.resources.root import add_example_process
    from .root import add_mercator_process
    from .root import mercator_root_meta
    assert add_mercator_process not in root_meta.after_creation
    assert add_mercator_process in mercator_root_meta.after_creation
    assert add_example_process in mercator_root_meta.after_creation
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
def test_initialize_workflow(registry, monkeypatch):
    from adhocracy_mercator.resources.root import initialize_workflow
    import adhocracy_core.workflows
    workflow = registry.content.workflows['mercator']
    get_workflow_mock = Mock(return_value=workflow)
    monkeypatch.setattr(adhocracy_core.workflows,
                        'get_workflow',
                        get_workflow_mock)
    root = testing.DummyResource()
    mercator = testing.DummyResource()
    root['mercator'] = mercator
    root.__acl__ = [(Allow, 'role:god', ALL_PERMISSIONS)]
    initialize_workflow(root, registry, {})
    assert workflow.state_of(mercator) == 'participate'
