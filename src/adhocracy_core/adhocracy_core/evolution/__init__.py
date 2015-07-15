"""Scripts to migrate legacy objects in existing databases."""
import logging
from functools import wraps
from pyramid.registry import Registry
from pyramid.threadlocal import get_current_registry
from zope.interface.interfaces import IInterface
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.interface import directlyProvides
from substanced.evolution import add_evolution_step
from substanced.util import find_service
from substanced.interfaces import IFolder
from adhocracy_core.utils import get_sheet
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import search_query
from adhocracy_core.interfaces import ResourceMetadata
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.badge import IHasBadgesPool
from adhocracy_core.sheets.badge import IBadgeable
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.resources.pool import IBasicPool
from adhocracy_core.resources.asset import IPoolWithAssets
from adhocracy_core.resources.badge import add_badges_service
from adhocracy_core.resources.badge import add_badge_assignments_service
from adhocracy_core.resources.principal import IUser
from adhocracy_core.catalog import ICatalogsService


logger = logging.getLogger(__name__)


def migrate_new_sheet(context: IPool,
                      iresource: IInterface,
                      isheet: IInterface,
                      isheet_old: IInterface=None,
                      remove_isheet_old=False,
                      fields_mapping: [(str, str)]=[]):
    """Add new `isheet` to `iresource` resources and migrate field values.

    :param context: Pool to search for `iresource` resources
    :param iresource: resource type to migrate
    :param isheet: new sheet interface to add
    :param isheet_old: old sheet interface to migrate,
        must not be None if `fields_mapping` or `remove_isheet_old` is set.
    :param remove_isheet_old: remove old sheet interface
    :param fields_mapping: list of (field name, old field name) to
                           migrate field values.
    """
    registry = get_current_registry(context)
    catalogs = find_service(context, 'catalogs')
    interfaces = isheet_old and (isheet_old, iresource) or iresource
    query = search_query._replace(interfaces=interfaces)
    resources = catalogs.search(query).elements
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


def migrate_new_iresource(context: IResource,
                          old_iresource: IInterface,
                          new_iresource: IInterface):
    """Migrate resources with `old_iresource` interface to `new_iresource`."""
    meta = _get_resource_meta(context, new_iresource)
    catalogs = find_service(context, 'catalogs')
    resources = _search_for_interfaces(catalogs, old_iresource)
    for resource in resources:
        logger.info('Migrate iresource of {0}'.format(resource))
        noLongerProvides(resource, old_iresource)
        directlyProvides(resource, new_iresource)
        for sheet in meta.basic_sheets + meta.extended_sheets:
            alsoProvides(resource, sheet)
        catalogs.reindex_index(resource, 'interfaces')


def _get_resource_meta(context: IResource,
                       iresource: IInterface) -> ResourceMetadata:
    registry = get_current_registry(context)
    meta = registry.content.resources_meta[iresource]
    return meta


def _search_for_interfaces(catalogs: ICatalogsService,
                           interfaces: (IInterface)) -> [IResource]:
    query = search_query._replace(interfaces=interfaces)
    resources = catalogs.search(query).elements
    return resources


def log_migration(func):
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


def _get_autonaming_prefixes(registry: Registry) -> [str]:
    """Return all autonaming_prefixes defined in the resources metadata."""
    meta = registry.content.resources_meta.values()
    prefixes = [m.autonaming_prefix for m in meta if m.use_autonaming]
    return list(set(prefixes))


@log_migration
def evolve1_add_title_sheet_to_pools(root: IPool):  # pragma: no cover
    """Add title sheet to basic pools and asset pools."""
    migrate_new_sheet(root, IBasicPool, ITitle)
    migrate_new_sheet(root, IPoolWithAssets, ITitle)


def add_kiezkassen_permissions(root):  # pragma: no cover
    """(disabled) Add permission to use the kiezkassen process."""


@log_migration
def upgrade_catalogs(root):  # pragma: no cover
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


@log_migration
def make_users_badgeable(root):  # pragma: no cover
    """Add badge services and make user badgeable."""
    registry = get_current_registry(root)
    principals = find_service(root, 'principals')
    if not IHasBadgesPool.providedBy(principals):
        logger.info('Add badges service to {0}'.format(principals))
        add_badges_service(principals, registry, {})
        alsoProvides(principals, IHasBadgesPool)
    users = find_service(root, 'principals', 'users')
    assignments = find_service(users, 'badge_assignments')
    if assignments is None:
        logger.info('Add badge assignments service to {0}'.format(users))
        add_badge_assignments_service(users, registry, {})
    migrate_new_sheet(root, IUser, IBadgeable)


@log_migration
def change_pools_autonaming_scheme(root):  # pragma: no cover
    """Change pool autonaming scheme."""
    registry = get_current_registry(root)
    prefixes = _get_autonaming_prefixes(registry)
    catalogs = find_service(root, 'catalogs')
    pools = _search_for_interfaces(catalogs, (IPool, IFolder))
    count = len(pools)
    for index, pool in enumerate(pools):
        logger.info('Migrating {0} of {1}: {2}'.format(index + 1, count, pool))
        if hasattr(pool, '_autoname_last'):
            pool._autoname_lasts = {prefix: pool._autoname_last
                                    for prefix in prefixes}
            del pool._autoname_last


@log_migration
def hide_password_resets(root):  # pragma: no cover
    """Add hide all password reset objects."""
    from adhocracy_core.resources.principal import hide
    from adhocracy_core.resources.principal import deny_view_permission
    registry = get_current_registry(root)
    resets = find_service(root, 'principals', 'resets')
    hidden = getattr(resets, 'hidden', False)
    if not hidden:
        logger.info('Deny view permission for {0}'.format(resets))
        deny_view_permission(resets, registry, {})

        logger.info('Hide {0}'.format(resets))
        hide(resets, registry, {})


@log_migration
def lower_case_users_emails(root):  # pragma: no cover
    """Lower case users email."""
    users = find_service(root, 'principals', 'users')
    for user in users.values():
        if not IUserExtended.providedBy(user):
            return
        sheet = get_sheet(user, IUserExtended)
        sheet.set({'email': user.email.lower()})
        # force update. Not working otherwise even if the sheet is set?!
        user._p_changed = True


@log_migration
def remove_name_sheet_from_items(root):  # pragma: no cover
    """Remove name sheet from items and items subtypes."""
    from adhocracy_core.sheets.name import IName
    from adhocracy_core.interfaces import IItem
    catalogs = find_service(root, 'catalogs')
    resources = _search_for_interfaces(catalogs, (IItem))
    count = len(resources)
    for index, resource in enumerate(resources):
        logger.info('Migrating {0} of {1}: {2}'.format(index + 1, count,
                                                       resource))
        logger.info('Remove {0} sheet'.format(IName))
        noLongerProvides(resource, IName)


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_directive('add_evolution_step', add_evolution_step)
    config.scan('substanced.evolution.subscribers')
    config.add_evolution_step(upgrade_catalogs)
    config.add_evolution_step(evolve1_add_title_sheet_to_pools)
    config.add_evolution_step(add_kiezkassen_permissions)
    config.add_evolution_step(make_users_badgeable)
    config.add_evolution_step(change_pools_autonaming_scheme)
    config.add_evolution_step(hide_password_resets)
    config.add_evolution_step(lower_case_users_emails)
    config.add_evolution_step(remove_name_sheet_from_items)
