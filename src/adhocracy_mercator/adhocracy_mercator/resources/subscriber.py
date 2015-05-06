"""Initialize Mercator ACM."""
from pyramid.events import ApplicationCreated
from pyramid.request import Request
from substanced.util import get_acl
from adhocracy_core.authorization import acm_to_acl
from adhocracy_core.utils import set_acl
from adhocracy_mercator.resources.mercator import mercator_acm
import transaction


def _application_created_subscriber(event):
    """Called when the Pyramid application is started."""
    app = event.app
    root = _get_root(app)
    _set_permissions(root, app.registry)


def _get_root(app):
    request = Request.blank('/path-is-meaningless-here')
    request.registry = app.registry
    root = app.root_factory(request)
    return root


def _set_permissions(root, registry):
    acl = get_acl(root)
    mercator_acl = acm_to_acl(mercator_acm, registry)
    new_acl = mercator_acl + acl
    set_acl(root, new_acl, registry)
    transaction.commit()  # otherwise mercator permission get discarded?!


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(_application_created_subscriber, ApplicationCreated)
