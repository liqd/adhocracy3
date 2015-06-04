from unittest.mock import Mock
from pyramid.security import Allow
from pyramid.security import Deny
from pyramid.security import ALL_PERMISSIONS
from pyramid import testing
from pytest import fixture
from pytest import mark
from adhocracy_core.interfaces import IResource

def test_application_created_subscriber(monkeypatch):
    import transaction
    import adhocracy_mercator.resources.subscriber
    commit_mock = Mock()
    mock_set_permissions = Mock()
    mock_initialize_workflow = Mock()
    monkeypatch.setattr(adhocracy_mercator.resources.subscriber,
                        '_set_permissions', mock_set_permissions)
    monkeypatch.setattr(adhocracy_mercator.resources.subscriber,
                        '_initialize_workflow', mock_initialize_workflow)
    monkeypatch.setattr(transaction, 'commit', commit_mock)
    event = Mock()
    from adhocracy_mercator.resources.subscriber import _application_created_subscriber
    _application_created_subscriber(event)
    assert mock_set_permissions.called
    assert commit_mock.called


def test_set_permissions():
    from adhocracy_mercator.resources.subscriber import _set_permissions
    app = Mock()
    app.registry.content.permissions = ['edit_proposal']
    root = testing.DummyResource(__acl__=[])
    app.root_factory.return_value = root
    _set_permissions(app)
    assert (Allow, 'role:admin', 'edit_proposal') in root.__acl__
    assert (Allow, 'role:god', ALL_PERMISSIONS) == root.__acl__[0]


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.rest')
    config.include('adhocracy_core.workflows.sample')
    config.include('adhocracy_mercator.workflows')


@mark.usefixtures('integration')
def test_initialize_workflow(registry):
    from adhocracy_mercator.resources.subscriber import _initialize_workflow
    app = Mock()
    root = testing.DummyResource()
    mercator = testing.DummyResource()
    root['mercator'] = mercator
    root.__acl__ = [(Allow, 'role:god', ALL_PERMISSIONS)]
    app.root_factory.return_value = root
    app.registry = registry
    workflow = registry.content.workflows['mercator']
    _initialize_workflow(app)
    assert workflow.state_of(mercator) == 'participate'
