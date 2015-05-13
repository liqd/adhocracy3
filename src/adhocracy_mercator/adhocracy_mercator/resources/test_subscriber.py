from unittest.mock import Mock
from pyramid.security import Allow
from pyramid.security import Deny
from pyramid import testing


def test_application_created_subscriber(monkeypatch):
    import transaction
    from adhocracy_mercator.resources.subscriber import _application_created_subscriber
    event = Mock()
    # avoid substanced querying the real registry when the commit occurs
    monkeypatch.setattr(transaction, 'commit', lambda: None)
    event.app.registry.content.permissions = ['edit_mercator_proposal']
    root = testing.DummyResource(__acl__=[(Allow, 'role:creator', 'view')])
    event.app.root_factory.return_value = root
    _application_created_subscriber(event)
    assert (Deny, 'role:creator', 'edit_mercator_proposal') in root.__acl__
    assert (Allow, 'role:creator', 'view') in root.__acl__
    assert (Allow, 'role:god', 'edit_mercator_proposal') in root.__acl__
