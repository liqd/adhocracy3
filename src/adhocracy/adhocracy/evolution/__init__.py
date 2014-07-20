""" Evolve scripts for the adhocracy application."""
import logging

from pyramid.threadlocal import get_current_registry
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from substanced.util import set_acl
from substanced.util import get_acl
from substanced.evolution import add_evolution_step


logger = logging.getLogger(__name__)


def add_app_root_element(root):
    """Add application root object to the zodb root."""
    logger.info(add_app_root_element.__doc__)
    reg = get_current_registry()
    if 'adhocracy' not in root:
        appstructs = {'adhocracy.sheets.name.IName': {'name': 'adhocracy'}}
        reg.content.create('adhocracy.resources.pool.IBasicPool',
                           root,
                           appstructs=appstructs,
                           )


def add_app_root_permissions(root):
    """Set permissions for the application root object."""
    logger.info(add_app_root_permissions.__doc__)
    app_root = root['adhocracy']
    acl = get_acl(app_root, [])
    acl.append((Allow, 'system.Everyone', ALL_PERMISSIONS))
    set_acl(app_root, acl)


def includeme(config):  # pragma: no cover
    """Run pyramid configuration."""
    config.add_evolution_step(add_app_root_element)
    config.add_evolution_step(
        add_app_root_permissions, after=add_app_root_element)
    config.add_directive('add_evolution_step', add_evolution_step)
    config.scan('substanced.evolution.subscribers')
