"""Initialize Mercator ACM."""
from pyramid.events import ApplicationCreated
from adhocracy_core.utils import get_root
from adhocracy_core.authorization import add_acm
from adhocracy_core.authorization import clean_acl
from adhocracy_core.authorization import set_god_all_permissions
from adhocracy_core.resources.root import root_acm
from adhocracy_mercator.resources.mercator import mercator_acm
import transaction


def _application_created_subscriber(event):
    """Called when the Pyramid application is started."""
    app = event.app
    root = get_root(app)
    clean_acl(root, app.registry)
    add_acm(root, root_acm, app.registry)
    add_acm(root, mercator_acm, app.registry)
    set_god_all_permissions(root, app.registry)
    transaction.commit()


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(_application_created_subscriber, ApplicationCreated)
