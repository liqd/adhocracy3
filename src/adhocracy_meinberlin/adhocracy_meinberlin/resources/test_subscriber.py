from unittest.mock import Mock
from pyramid.security import Allow
from pyramid.security import Deny
from pyramid import testing


def test_application_created_subscriber(monkeypatch):
    import transaction
    from adhocracy_meinberlin.resources.subscriber import _application_created_subscriber
    event = Mock()
    # avoid substanced querying the real registry when the commit occurs
    monkeypatch.setattr(transaction, 'commit', lambda: None)
    event.app.registry.content.permissions = ['edit_proposal',
                                              'create_proposal'
                                              'create_process']
    root = testing.DummyResource(__acl__=[(Allow, 'role:creator', 'view')])
    event.app.root_factory.return_value = root
    _application_created_subscriber(event)
    assert (Allow, 'role:admin', 'create_proposal') in root.__acl__
