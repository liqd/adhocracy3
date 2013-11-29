#
# Evolve scripts for the adhocracy application
#
import logging
from pyramid.threadlocal import get_current_registry
from pyramid.security import (
    Allow,
    ALL_PERMISSIONS,
    )
from substanced.util import (
    set_acl,
    get_acl
    )


logger = logging.getLogger('evolution')

def add_app_root_element(root):
    logger.info(
        'Add application root object to the zodb root'
    )
    reg = get_current_registry()
    if "adhocracy" not in root:
        root["adhocracy"] = reg.content.create("adhocracy.resources.interfaces.IPool")

def add_app_root_permissions(root):
    logger.info(
        'Set permissions for the application root object'
    )
    app_root = root["adhocracy"]
    acl = get_acl(app_root, [])
    acl.append((Allow, 'system.Everyone', ALL_PERMISSIONS))
    set_acl(app_root, acl)

def includeme(config):
    config.add_evolution_step(add_app_root_element)
    config.add_evolution_step(add_app_root_permissions, after=add_app_root_element)

