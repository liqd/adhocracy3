"""Initialize meinberlin ACM."""
from pyramid.events import ApplicationCreated
from adhocracy_core.authorization import add_acm
from adhocracy_core.utils import get_root
from adhocracy_meinberlin.resources.root import meinberlin_acm
import transaction


def _application_created_subscriber(event):
    """Called when the Pyramid application is started."""
    app = event.app
    root = get_root(app)
    add_acm(root, meinberlin_acm, app.registry)
    transaction.commit()


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(_application_created_subscriber, ApplicationCreated)
