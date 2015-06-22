"""Initialize Mercator ACM."""
from pyramid.events import ApplicationCreated
from adhocracy_core.authorization import set_acms_for_app_root
from adhocracy_core.resources.root import root_acm
from adhocracy_mercator.resources.root import mercator_acm


def set_root_acms(event):
    """Set :term:`acm`s for root if the Pyramid application starts."""
    set_acms_for_app_root(event.app, (mercator_acm, root_acm))


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(set_root_acms, ApplicationCreated)
