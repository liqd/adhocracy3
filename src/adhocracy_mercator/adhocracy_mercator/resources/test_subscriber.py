from unittest.mock import Mock
from pyramid.security import Allow
from pyramid import testing

def test_application_created_subscriber():
    from adhocracy_mercator.resources.subscriber import _application_created_subscriber
    event = Mock()
    event.app.registry.content.permissions = ['add_mercator_proposal_version']
    root = testing.DummyResource(__acl__=[(Allow, 'role:creator', 'view')])
    event.app.root_factory.return_value = root
    _application_created_subscriber(event)
    assert (Allow, 'role:creator', 'add_mercator_proposal_version') in root.__acl__
    assert (Allow, 'role:creator', 'view') in root.__acl__
    assert (Allow, 'role:god', 'add_mercator_proposal_version') in root.__acl__
