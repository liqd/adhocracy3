"""Initialize Mercator ACM."""
from pyramid.events import ApplicationCreated
from adhocracy_core.utils import get_root
from adhocracy_core.authorization import add_acm
from adhocracy_core.authorization import clean_acl
from adhocracy_core.authorization import set_god_all_permissions
from adhocracy_core.resources.root import root_acm
from adhocracy_mercator.resources.root import mercator_acm
import transaction
from pyramid.request import Request


def _application_created_subscriber(event):
    """Called when the Pyramid application is started."""
    app = event.app
    _set_permissions(app)
    _initialize_workflow(app)
    transaction.commit()


def _set_permissions(app):
    root = get_root(app)
    clean_acl(root, app.registry)
    add_acm(root, root_acm, app.registry)
    add_acm(root, mercator_acm, app.registry)
    set_god_all_permissions(root, app.registry)


def _initialize_workflow(app):
    root = get_root(app)
    registry = app.registry
    request = Request.blank('/dummy')
    request.root = root
    request.registry = registry
    request.__cached_principals__ = ['role:god']
    mercator_process = root['mercator']
    workflow = registry.content.workflows['mercator']
    workflow.initialize(mercator_process)
    workflow.transition_to_state(mercator_process, request, 'announce')
    workflow.transition_to_state(mercator_process, request, 'participate')


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(_application_created_subscriber, ApplicationCreated)
