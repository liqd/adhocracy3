"""Scripts to migrate legacy objects in existing databases."""
import logging
from functools import wraps
from pyramid.registry import Registry
from pyramid.threadlocal import get_current_registry
from pyramid.security import Allow
from zope.interface.interfaces import IInterface
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from substanced.evolution import add_evolution_step
from substanced.util import get_acl
from adhocracy_core.utils import get_sheet
from adhocracy_core.authorization import set_acl
from adhocracy_core.interfaces import IResource
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.resources.pool import IBasicPool
from adhocracy_core.resources.asset import IPoolWithAssets
from adhocracy_core.catalog import ICatalogsService


logger = logging.getLogger(__name__)


def migrate_new_sheet(context: IPool,
                      iresource: IInterface,
                      isheet: IInterface,
                      isheet_old: IInterface,
                      remove_isheet_old=False,
                      fields_mapping: [(str, str)]=[]):
    """Add new `isheet` to `iresource` resources and migrate field values.

    :param context: Pool to search for `iresource` resources
    :param iresource: resource type to migrate
    :param isheet: new sheet interface to add
    :param isheet_old: old sheet interface
    :param remove_isheet_old: remove old sheet interface
    :param fields_mapping: list of (field name, old field name) to
                           migrate field values.
    """
    registry = get_current_registry(context)
    pool = get_sheet(context, IPool, registry=registry)
    query = {'interfaces': (isheet_old, iresource),
             'only_visible': False,
             'depth': 0
             }
    resources = pool.get(query)['elements']
    count = len(resources)
    logger.info('Migrating {0} {1} to new sheet {2}'.format(count, iresource,
                                                            isheet))
    for index, resource in enumerate(resources):
        logger.info('Migrating {0} of {1}: {2}'.format(index + 1, count,
                                                       resource))
        logger.info('Add {0}  sheet'.format(isheet))
        alsoProvides(resource, isheet)
        if fields_mapping:
            _migrate_field_values(registry, resource, isheet, isheet_old,
                                  fields_mapping)
        if remove_isheet_old:
            logger.info('Remove {0} sheet'.format(isheet_old))
            noLongerProvides(resource, isheet_old)


def migration_script(func):
    """Decorator for the migration scripts.

    The decorator logs the call to the evolve script.
    """
    logger = logging.getLogger(func.__module__)

    @wraps(func)
    def logger_decorator(*args, **kwargs):
        logger.info('Running evolve step: ' + func.__doc__)
        func(*args, **kwargs)
        logger.info('Finished evolve step: ' + func.__doc__)

    return logger_decorator


def _migrate_field_values(registry: Registry, resource: IResource,
                          isheet: IInterface, isheet_old: IInterface,
                          fields_mapping=[(str, str)]):
    sheet = get_sheet(resource, isheet, registry=registry)
    old_sheet = get_sheet(resource, isheet_old, registry=registry)
    appstruct = {}
    for field, old_field in fields_mapping:
        logger.info('Migrate value for field {0}'.format(field))
        appstruct[field] = old_sheet.get()[old_field]
        old_sheet.delete_field_values([old_field])
    sheet.set(appstruct)


@migration_script
def evolve1_add_title_sheet_to_pools(root: IPool):  # pragma: no cover
    """Add title sheet to basic pools and asset pools."""
    migrate_new_sheet(root, IBasicPool, ITitle, IPool,
                      remove_isheet_old=False)
    migrate_new_sheet(root, IPoolWithAssets, ITitle, IPool,
                      remove_isheet_old=False)


@migration_script
def add_kiezkassen_permissions(root):
    """Add permission to use the kiezkassen process."""
    registry = get_current_registry()
    acl = get_acl(root)
    new_acl = [(Allow, 'role:contributor', 'add_kiezkassen_proposal'),
               (Allow, 'role:creator', 'edit_kiezkassen_proposal'),
               (Allow, 'role:admin', 'add_kiezkassen_process'),
               (Allow, 'role:admin', 'add_process')]
    updated_acl = acl + new_acl
    set_acl(root, updated_acl, registry=registry)


@migration_script
def upgrade_catalogs(root):
    """Upgrade catalogs."""
    registry = get_current_registry()
    old_catalogs = root['catalogs']

    old_catalogs.move('system', root, 'old_system_catalog')
    old_catalogs.move('adhocracy', root, 'old_adhocracy_catalog')

    del root['catalogs']

    registry.content.create(ICatalogsService.__identifier__, parent=root)

    catalogs = root['catalogs']
    del catalogs['system']
    del catalogs['adhocracy']
    root.move('old_system_catalog', catalogs, 'system')
    root.move('old_adhocracy_catalog', catalogs, 'adhocracy')

    catalogs.reindex_all(catalogs['system'])
    catalogs.reindex_all(catalogs['adhocracy'])


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_directive('add_evolution_step', add_evolution_step)
    config.scan('substanced.evolution.subscribers')
    config.add_evolution_step(upgrade_catalogs)
    config.add_evolution_step(evolve1_add_title_sheet_to_pools)
    config.add_evolution_step(add_kiezkassen_permissions)
