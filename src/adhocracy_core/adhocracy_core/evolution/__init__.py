"""Scripts to migrate legacy objects in existing databases."""
import logging
from functools import wraps

from BTrees.Length import Length
from persistent.mapping import PersistentMapping
from pyramid.registry import Registry
from pyramid.threadlocal import get_current_registry
from substanced.evolution import add_evolution_step
from substanced.interfaces import IFolder
from substanced.util import find_service
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import noLongerProvides
from zope.interface.interfaces import IInterface

from adhocracy_core.resources.principal import allow_create_asset_authenticated
from adhocracy_core.catalog import ICatalogsService
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import ISimple
from adhocracy_core.interfaces import ResourceMetadata
from adhocracy_core.interfaces import search_query
from adhocracy_core.resources.asset import IAsset
from adhocracy_core.resources.asset import IPoolWithAssets
from adhocracy_core.resources.asset import add_assets_service
from adhocracy_core.resources.badge import IBadgeAssignmentsService
from adhocracy_core.resources.badge import add_badge_assignments_service
from adhocracy_core.resources.badge import add_badges_service
from adhocracy_core.resources.comment import ICommentVersion
from adhocracy_core.resources.organisation import IOrganisation
from adhocracy_core.resources.pool import IBasicPool
from adhocracy_core.resources.principal import IUser
from adhocracy_core.resources.principal import IUsersService
from adhocracy_core.resources.process import IProcess
from adhocracy_core.resources.proposal import IProposal
from adhocracy_core.resources.proposal import IProposalVersion
from adhocracy_core.resources.relation import add_relationsservice
from adhocracy_core.sheets.asset import IHasAssetPool
from adhocracy_core.sheets.badge import IBadgeable
from adhocracy_core.sheets.badge import IHasBadgesPool
from adhocracy_core.sheets.badge import ICanBadge
from adhocracy_core.sheets.description import IDescription
from adhocracy_core.sheets.image import IImageReference
from adhocracy_core.sheets.notification import IFollowable
from adhocracy_core.sheets.notification import INotification
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.sheets.relation import ICanPolarize
from adhocracy_core.sheets.relation import IPolarizable
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.workflows import update_workflow_state_acls

logger = logging.getLogger(__name__)


def migrate_to_attribute_storage(context: IPool, isheet: IInterface):
    """Migrate sheet data for`isheet` from annotation to attribute storage."""
    registry = get_current_registry(context)
    sheet_meta = registry.content.sheets_meta[isheet]
    isheet_name = sheet_meta.isheet.__identifier__
    annotation_key = '_sheet_' + isheet_name.replace('.', '_')
    catalogs = find_service(context, 'catalogs')
    resources = _search_for_interfaces(catalogs, isheet)
    count = len(resources)
    logger.info('Migrating {0} resources with {1} to attribute storage'
                .format(count, isheet))
    for index, resource in enumerate(resources):
        data = resource.__dict__
        if annotation_key in data:
            logger.info('Migrating resource {0} of {1}'
                        .format(index + 1, count))
            for field, value in data[annotation_key].items():
                setattr(resource, field, value)
            delattr(resource, annotation_key)


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
    query = search_query._replace(interfaces=interfaces,
                                  resolve=True)
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
        catalogs.reindex_index(resource, 'interfaces')


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
    query = search_query._replace(interfaces=interfaces, resolve=True)
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
    sheet = registry.content.get_sheet(resource, isheet)
    old_sheet = registry.content.get_sheet(resource, isheet_old)
    appstruct = {}
    for field, old_field in fields_mapping:
        old_appstruct = old_sheet.get()
        if old_field in old_appstruct:
            logger.info('Migrate value for field {0}'.format(field))
            appstruct[field] = old_appstruct[old_field]
            old_sheet.delete_field_values([old_field])
    sheet.set(appstruct)


def _get_autonaming_prefixes(registry: Registry) -> [str]:
    """Return all autonaming_prefixes defined in the resources metadata."""
    meta = registry.content.resources_meta.values()
    prefixes = [m.autonaming_prefix for m in meta if m.use_autonaming]
    return list(set(prefixes))


def _get_used_autonaming_prefixes(pool: IPool,  # pragma: no cover
                                  prefixes: [str]) -> [str]:
    used_prefixes = set()
    for child_name in pool:
        for prefix in prefixes:
            if child_name.startswith(prefix):
                used_prefixes.add(prefix)
    return list(used_prefixes)


@log_migration
def evolve1_add_title_sheet_to_pools(root: IPool,
                                     registry: Registry):  # pragma: no cover
    """Add title sheet to basic pools and asset pools."""
    migrate_new_sheet(root, IBasicPool, ITitle)
    migrate_new_sheet(root, IPoolWithAssets, ITitle)


def add_kiezkassen_permissions(root):  # pragma: no cover
    """(disabled) Add permission to use the kiezkassen process."""


@log_migration
def upgrade_catalogs(root, registry):  # pragma: no cover
    """Upgrade catalogs."""
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
def make_users_badgeable(root, registry):  # pragma: no cover
    """Add badge services and make user badgeable."""
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
def make_proposals_badgeable(root, registry):  # pragma: no cover
    """Add badge services processes and make proposals badgeable."""
    catalogs = find_service(root, 'catalogs')
    proposals = _search_for_interfaces(catalogs, IProposal)
    for proposal in proposals:
        if not IBadgeable.providedBy(proposal):
            logger.info('add badgeable interface to {0}'.format(proposal))
            alsoProvides(proposal, IBadgeable)
        if 'badge_assignments' not in proposal:
            logger.info('add badge assignments to {0}'.format(proposal))
            add_badge_assignments_service(proposal, registry, {})
    processes = _search_for_interfaces(catalogs, IProcess)
    for process in processes:
        if not IHasBadgesPool.providedBy(process):
            logger.info('Add badges service to {0}'.format(process))
            add_badges_service(process, registry, {})
            alsoProvides(process, IHasBadgesPool)


@log_migration
def change_pools_autonaming_scheme(root, registry):  # pragma: no cover
    """Change pool autonaming scheme."""
    prefixes = _get_autonaming_prefixes(registry)
    catalogs = find_service(root, 'catalogs')
    pools = _search_for_interfaces(catalogs, (IPool, IFolder))
    count = len(pools)
    for index, pool in enumerate(pools):
        logger.info('Migrating {0} of {1}: {2}'.format(index + 1, count, pool))
        if not pool:
            continue
        if hasattr(pool, '_autoname_last'):
            pool._autoname_lasts = PersistentMapping()
            for prefix in prefixes:
                pool._autoname_lasts[prefix] = Length(pool._autoname_last + 1)
            del pool._autoname_last
        elif not hasattr(pool, '_autoname_lasts'):
            pool._autoname_lasts = PersistentMapping()
            for prefix in prefixes:
                pool._autoname_lasts[prefix] = Length()
        if hasattr(pool, '_autoname_lasts'):
            # convert int to Length
            for prefix in pool._autoname_lasts.keys():
                if isinstance(pool._autoname_lasts[prefix], int):
                    pool._autoname_lasts[prefix] \
                        = Length(pool._autoname_lasts[prefix].value)
                elif isinstance(pool._autoname_lasts[prefix].value, Length):
                    pool._autoname_lasts[prefix] = Length(1)
            # convert dict to PersistentMapping
            if not isinstance(pool._autoname_lasts, PersistentMapping):
                pool._autoname_lasts = PersistentMapping(pool._autoname_lasts)


@log_migration
def hide_password_resets(root, registry):  # pragma: no cover
    """Add hide all password reset objects."""
    from adhocracy_core.resources.principal import hide
    from adhocracy_core.resources.principal import deny_view_permission
    resets = find_service(root, 'principals', 'resets')
    hidden = getattr(resets, 'hidden', False)
    if not hidden:
        logger.info('Deny view permission for {0}'.format(resets))
        deny_view_permission(resets, registry, {})

        logger.info('Hide {0}'.format(resets))
        hide(resets, registry, {})


@log_migration
def lower_case_users_emails(root, registry):  # pragma: no cover
    """Lower case users email, add 'private_user_email'/'user_name' index."""
    _update_adhocracy_catalog(root)
    catalogs = find_service(root, 'catalogs')
    users = find_service(root, 'principals', 'users')
    for user in users.values():
        if not IUserExtended.providedBy(user):
            return
        sheet = registry.content.get_sheet(user, IUserExtended)
        sheet.set({'email': user.email.lower()})
        catalogs.reindex_index(user, 'private_user_email')
        catalogs.reindex_index(user, 'user_name')


def _update_adhocracy_catalog(root):  # pragma: no cover
    """Add/Remove indexes for catalog `adhocracy`."""
    adhocracy = find_service(root, 'catalogs', 'adhocracy')
    adhocracy.update_indexes()


@log_migration
def remove_name_sheet_from_items(root, registry):  # pragma: no cover
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


@log_migration
def add_workflow_assignment_sheet_to_pools_simples(
        root, registry):  # pragma: no cover
    """Add generic workflow sheet to pools and simples."""
    migrate_new_sheet(root, IPool, IWorkflowAssignment)
    migrate_new_sheet(root, ISimple, IWorkflowAssignment)


@log_migration
def make_proposalversions_polarizable(root, registry):  # pragma: no cover
    """Make proposals polarizable and add relations pool."""
    catalogs = find_service(root, 'catalogs')
    proposals = _search_for_interfaces(catalogs, IProposal)
    for proposal in proposals:
        if 'relations' not in proposal:
            logger.info('add relations pool to {0}'.format(proposal))
            add_relationsservice(proposal, registry, {})
    migrate_new_sheet(root, IProposalVersion, IPolarizable)


@log_migration
def add_icanpolarize_sheet_to_comments(root, registry):  # pragma: no cover
    """Make comments ICanPolarize."""
    migrate_new_sheet(root, ICommentVersion, ICanPolarize)


@log_migration
def migrate_rate_sheet_to_attribute_storage(root,
                                            registry):  # pragma: no cover
    """Migrate rate sheet to attribute storage."""
    import adhocracy_core.sheets.rate
    migrate_to_attribute_storage(root, adhocracy_core.sheets.rate.IRate)


@log_migration
def move_autoname_last_counters_to_attributes(root,
                                              registry):  # pragma: no cover
    """Move autoname last counters of pools to attributes.

    Remove _autoname_lasts attribute.
    Instead add private attributes to store autoname last counter objects.
    Cleanup needless counter objects.
    """
    prefixes = _get_autonaming_prefixes(registry)
    catalogs = find_service(root, 'catalogs')
    pools = _search_for_interfaces(catalogs, (IPool, IFolder))
    count = len(pools)
    for index, pool in enumerate(pools):
        logger.info('Migrating resource {0} {1} of {2}'
                    .format(pool, index + 1, count))
        if hasattr(pool, '_autoname_last'):
            logger.info('Remove "_autoname_last" attribute')
            delattr(pool, '_autoname_last')
        if hasattr(pool, '_autoname_lasts'):
            used_prefixes = _get_used_autonaming_prefixes(pool, prefixes)
            for prefix in used_prefixes:
                is_badge_service = IBadgeAssignmentsService.providedBy(pool)
                if prefix == '' and not is_badge_service:
                    continue
                logger.info('Move counter object for prefix {0} to attribute'
                            .format(prefix))
                counter = pool._autoname_lasts.get(prefix, Length())
                if isinstance(counter, int):
                    counter = Length(counter)
                setattr(pool, '_autoname_last_' + prefix, counter)
            logger.info('Remove "_autoname_lasts" attribute')
            delattr(pool, '_autoname_lasts')


@log_migration
def move_sheet_annotation_data_to_attributes(root,
                                             registry):  # pragma: no cover
    """Move sheet annotation data to resource attributes.

    Remove `_sheets` dictionary to store sheets data annotations.
    Instead add private attributes for every sheet data annotation to resource.
    """
    catalogs = find_service(root, 'catalogs')
    query = search_query._replace(interfaces=(IResource,), resolve=True)
    resources = catalogs.search(query).elements
    count = len(resources)
    for index, resource in enumerate(resources):
        if not hasattr(resource, '_sheets'):
            continue
        logger.info('Migrating resource {0} of {1}'.format(index + 1, count))
        for data_key, appstruct in resource._sheets.items():
            annotation_key = '_sheet_' + data_key.replace('.', '_')
            if appstruct:
                setattr(resource, annotation_key, appstruct)
        delattr(resource, '_sheets')


@log_migration
def add_image_reference_to_users(root, registry):  # pragma: no cover
    """Add image reference to users and add assets service to users service."""
    users = find_service(root, 'principals', 'users')
    if not IHasAssetPool.providedBy(users):
        logger.info('Add assets service to {0}'.format(users))
        add_assets_service(users, registry, {})
    migrate_new_sheet(root, IUsersService, IHasAssetPool)
    migrate_new_sheet(root, IUser, IImageReference)


def remove_empty_first_versions(root, registry):  # pragma: no cover
    """Outdated."""


@log_migration
def update_asset_download_children(root, registry):  # pragma: no cover
    """Add asset downloads and update IAssetMetadata sheet."""
    from adhocracy_core.sheets.asset import IAssetMetadata
    from adhocracy_core.sheets.image import IImageMetadata
    from adhocracy_core.resources.asset import add_metadata
    from adhocracy_core.resources.image import add_image_size_downloads
    catalogs = find_service(root, 'catalogs')
    assets = _search_for_interfaces(catalogs, IAsset)
    count = len(assets)
    for index, asset in enumerate(assets):
        logger.info('Migrating resource {0} of {1}'.format(index + 1, count))
        old_downloads = [x for x in asset]
        for old in old_downloads:
            del asset[old]
        try:
            if IAssetMetadata.providedBy(asset):
                add_metadata(asset, registry)
            if IImageMetadata.providedBy(asset):
                add_image_size_downloads(asset, registry)
        except AttributeError:
            logger.warn('Asset {} has no downloads to migrate.'.format(asset))


@log_migration
def recreate_all_image_size_downloads(root, registry):  # pragma: no cover
    """Recreate all image size downloads to optimize file size."""
    from adhocracy_core.sheets.asset import IAssetMetadata
    from adhocracy_core.sheets.image import IImageMetadata
    from adhocracy_core.resources.image import add_image_size_downloads
    from adhocracy_core.resources.image import IImageDownload
    catalogs = find_service(root, 'catalogs')
    assets = _search_for_interfaces(catalogs, IAssetMetadata)
    images = [x for x in assets if IImageMetadata.providedBy(x)]
    count = len(images)
    for index, image in enumerate(images):
        logger.info('Migrating resource {0} of {1}'.format(index + 1, count))
        for old_download in image.values():
            if IImageDownload.providedBy(old_download):
                del image[old_download.__name__]
        add_image_size_downloads(image, registry)
        catalogs.reindex_index(image, 'interfaces')  # we missed reindexing


@log_migration
def remove_tag_resources(root, registry):  # pragma: no cover
    """Remove all ITag resources, create ITags sheet references instead."""
    from adhocracy_core.sheets.tags import ITags
    from adhocracy_core.interfaces import IItem
    catalogs = find_service(root, 'catalogs')
    items = _search_for_interfaces(catalogs, IItem)
    items_with_tags = [x for x in items if 'FIRST' in x]
    count = len(items_with_tags)
    for index, item in enumerate(items_with_tags):
        logger.info('Migrate tag resource {0} of {1}'.format(index + 1, count))
        del item['FIRST']
        del item['LAST']
        version_names = [x[0] for x in item.items()
                         if IItemVersion.providedBy(x[1])]
        version_names.sort()  # older version names are lower then younger ones
        first_version = version_names[0]
        last_version = version_names[-1]
        tags_sheet = registry.content.get_sheet(item, ITags)
        tags_sheet.set({'LAST': item[last_version],
                        'FIRST': item[first_version]})


@log_migration
def reindex_interfaces_catalog_for_root(root, registry):  # pragma: no cover
    """Reindex 'interfaces' catalog for root."""
    catalogs = find_service(root, 'catalogs')
    catalogs.reindex_index(root, 'interfaces')


@log_migration
def add_description_sheet_to_organisations(root, registry):  # pragma: no cover
    """Add description sheet to organisations."""
    migrate_new_sheet(root, IOrganisation, IDescription)


@log_migration
def add_description_sheet_to_processes(root, registry):  # pragma: no cover
    """Add description sheet to processes."""
    migrate_new_sheet(root, IProcess, IDescription)


@log_migration
def add_image_reference_to_organisations(root, registry):  # pragma: no cover
    """Add image reference to organisations and add assets service."""
    catalogs = find_service(root, 'catalogs')
    query = search_query._replace(interfaces=(IOrganisation,), resolve=True)
    organisations = catalogs.search(query).elements
    for organisation in organisations:
        if not IHasAssetPool.providedBy(organisation):
            logger.info('Add assets service to {0}'.format(organisation))
            add_assets_service(organisation, registry, {})
    migrate_new_sheet(root, IOrganisation, IHasAssetPool)
    migrate_new_sheet(root, IOrganisation, IImageReference)


def set_comment_count(root, registry):  # pragma: no cover
    """Outdated."""


def remove_duplicated_group_ids(root, registry):  # pragma: no cover
    """Remove duplicate group_ids from users."""
    from adhocracy_core.resources.principal import IUser
    catalogs = find_service(root, 'catalogs')
    users = _search_for_interfaces(catalogs, IUser)
    count = len(users)
    for index, user in enumerate(users):
        logger.info('Migrate user resource{0} of {1}'.format(index + 1, count))
        group_ids = getattr(user, 'group_ids', [])
        if not group_ids:
            continue
        unique_group_ids = list(set(group_ids))
        if len(unique_group_ids) < len(group_ids):
            logger.info('Remove duplicated groupd_ids for {0}'.format(user))
            user.group_ids = unique_group_ids


@log_migration
def add_image_reference_to_proposals(root, registry):  # pragma: no cover
    """Add description sheet to proposals."""
    migrate_new_sheet(root, IProposalVersion, IImageReference)


def reset_comment_count(root, registry):  # pragma: no cover
    """Outdated."""


@log_migration
def remove_is_service_attribute(root, registry):  # pragma: no cover
    """Remove __is_service__ attribute, use IService interface instead."""
    from adhocracy_core.interfaces import IServicePool
    catalogs = find_service(root, 'catalogs')
    for catalog in catalogs.values():
        if hasattr(catalog, '__is_service__'):
            delattr(catalog, '__is_service__')
        alsoProvides(catalogs, IServicePool)
        catalogs.reindex_index(catalog, 'interfaces')
    services = _search_for_interfaces(catalogs, IServicePool)
    for service in services:
        if hasattr(service, '__is_service__'):
            delattr(service, '__is_service__')


@log_migration
def add_canbadge_sheet_to_users(root, registry):  # pragma: no cover
    """Add canbadge sheet to users."""
    migrate_new_sheet(root, IUser, ICanBadge)


def enable_order_for_organisation(root, registry):  # pragma: no cover
    """Enable children order for organisations."""
    from adhocracy_core.resources.organisation import IOrganisation
    from adhocracy_core.resources.organisation import enabled_ordering
    catalogs = find_service(root, 'catalogs')
    resources = _search_for_interfaces(catalogs, IOrganisation)
    for resource in resources:
        logger.info('Enable ordering for {0}'.format(resource))
        enabled_ordering(resource, registry)


@log_migration
def allow_create_asset_for_users(root, registry):  # pragma: no cover
    """Allow all users to create_assets inside the users service."""
    users = find_service(root, 'principals', 'users')
    allow_create_asset_authenticated(users, registry, {})


@log_migration
def update_workflow_state_acl_for_all_resources(root,
                                                registry):  # pragma: no cover
    """Update the local :term:`acl` with the current workflow state acl."""
    update_workflow_state_acls(root, registry)


@log_migration
def add_controversiality_index(root, registry):  # pragma: no cover
    """Add controversity index."""
    from adhocracy_core.sheets.rate import IRateable
    catalogs = find_service(root, 'catalogs')
    catalog = catalogs['adhocracy']
    catalog.update_indexes(registry=registry)
    resources = _search_for_interfaces(catalogs, IRateable)
    index = catalog['controversiality']
    for resource in resources:
        index.reindex_resource(resource)


@log_migration
def add_description_sheet_to_user(root, registry):  # pragma: no cover
    """Add description sheet to user."""
    migrate_new_sheet(root, IUser, IDescription)


@log_migration
def remove_token_storage(root, registry):  # pragma: no cover
    """Remove storage for authentication tokens, not used anymore."""
    if hasattr(root, '_tokenmanager_storage'):
        delattr(root, '_tokenmanager_storage')


@log_migration
def set_default_workflow(root, registry):  # pragma: no cover
    """Set default workflow if no workflow in IWorkflowAssignment sheet."""
    from adhocracy_core.utils import get_iresource
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    catalogs = find_service(root, 'catalogs')
    resources = _search_for_interfaces(catalogs, IWorkflowAssignment)
    for resource in resources:
        iresource = get_iresource(resource)
        meta = registry.content.resources_meta[iresource]
        default_workflow_name = meta.default_workflow
        sheet = registry.content.get_sheet(resource, IWorkflowAssignment)
        workflow_name = sheet.get()['workflow']
        if not workflow_name and default_workflow_name:
            logger.info('Set default workflow {0} for {1}'.format(
                default_workflow_name, resource))
            sheet._store_data({'workflow': meta.default_workflow},
                              initialize_workflow=False)


@log_migration
def add_local_roles_for_workflow_state(root,
                                       registry):  # pragma: no cover
    """Add local role of the current workflow state for all processes."""
    from adhocracy_core.authorization import add_local_roles
    from adhocracy_core.resources.process import IProcess
    catalogs = find_service(root, 'catalogs')
    resources = _search_for_interfaces(catalogs, IProcess)
    count = len(resources)
    for index, resource in enumerate(resources):
        workflow = registry.content.get_workflow(resource)
        state_name = workflow.state_of(resource)
        local_roles = workflow._states[state_name].local_roles
        logger.info('Update workflow local roles for resource {0} - {1} of {2}'
                    .format(resource, index + 1, count))
        if local_roles:
            add_local_roles(resource, local_roles, registry=registry)


@log_migration
def rename_default_group(root, registry):  # pragma: no cover
    """Rename default user group."""
    from adhocracy_core.authorization import add_local_roles
    from adhocracy_core.authorization import get_local_roles
    from adhocracy_core.authorization import set_local_roles
    from adhocracy_core.resources.process import IProcess
    from adhocracy_core.interfaces import DEFAULT_USER_GROUP_NAME
    from adhocracy_core.sheets.principal import IPermissions
    catalogs = find_service(root, 'catalogs')
    resources = _search_for_interfaces(catalogs, IProcess)
    old_default_group_name = 'authenticated'
    old_default_group_principal = 'group:' + old_default_group_name
    new_default_group_name = DEFAULT_USER_GROUP_NAME
    new_default_group_principal = 'group:' + DEFAULT_USER_GROUP_NAME
    groups = root['principals']['groups']
    if old_default_group_name in groups:
        for resource in resources:
            local_roles = get_local_roles(resource)
            if old_default_group_principal in local_roles:
                logger.info('Rename default group in local roles'
                            ' of {0}'.format(resource))
                old_roles = local_roles.pop(old_default_group_principal)
                set_local_roles(resource, local_roles)
                add_local_roles({new_default_group_principal: old_roles})
        users = [u for u in root['principals']['users'].values()
                 if IPermissions.providedBy(u)]
        old_default_group = groups[old_default_group_name]
        users_with_default_group = []
        for user in users:
            user_groups = registry.content.get_sheet_field(user,
                                                           IPermissions,
                                                           'groups')
            if old_default_group in user_groups:
                users_with_default_group.append(user)
        logger.info('Rename default group '
                    'to {}'.format(new_default_group_name))
        groups.rename(old_default_group_name, new_default_group_name)
        new_default_group = groups[new_default_group_name]
        for user in users_with_default_group:
            logger.info('Update default group name of user {}'.format(user))
            permission_sheet = registry.content.get_sheet(user, IPermissions)
            permissions = permission_sheet.get()
            user_groups = permissions['groups']
            user_groups.append(new_default_group)
            permissions['groups'] = user_groups
            permission_sheet.set(permissions)


def migrate_auditlogentries_to_activities(root, registry):  # pragma: no cover
    """Replace AuditlogenEntries with Activities entries."""
    from pytz import UTC
    from adhocracy_core.interfaces import SerializedActivity
    from adhocracy_core.interfaces import ActivityType
    from adhocracy_core.interfaces import AuditlogEntry
    from adhocracy_core.interfaces import AuditlogAction
    from adhocracy_core.auditing import get_auditlog
    auditlog = get_auditlog(root)
    old_entries = [(key, value) for key, value in auditlog.items()]
    auditlog.clear()
    mapping = {AuditlogAction.concealed: ActivityType.remove,
               AuditlogAction.invisible: ActivityType.remove,
               AuditlogAction.revealed: ActivityType.update,
               AuditlogAction.created: ActivityType.add,
               AuditlogAction.modified: ActivityType.update,
               (AuditlogAction.concealed,): ActivityType.remove,
               (AuditlogAction.invisible,): ActivityType.remove,
               (AuditlogAction.revealed,): ActivityType.update,
               (AuditlogAction.created,): ActivityType.add,
               (AuditlogAction.modified,): ActivityType.update,
               }
    for key, value in old_entries:
        if not isinstance(value, AuditlogEntry):
            break
        new_value_kwargs = {'type': mapping.get(value.name),
                            'object_path': value.resource_path,
                            'subject_path': value.user_path or '',
                            'sheet_data': value.sheet_data or [],
                            }
        new_key = key.replace(tzinfo=UTC)
        auditlog[new_key] = SerializedActivity()._replace(**new_value_kwargs)


@log_migration
def add_notification_sheet_to_user(root, registry):  # pragma: no cover
    """Add notification sheet to user."""
    migrate_new_sheet(root, IUser, INotification)


@log_migration
def add_followable_sheet_to_process(root, registry):  # pragma: no cover
    """Add followable sheet to process."""
    migrate_new_sheet(root, IProcess, IFollowable)


@log_migration
def remove_comment_count_data(root, registry):  # pragma: no cover
    """Remove comment_count data in ICommentable sheet."""
    from adhocracy_core.sheets.comment import ICommentable
    catalogs = find_service(root, 'catalogs')
    commentables = _search_for_interfaces(catalogs, ICommentable)
    for commentable in commentables:
        sheet = registry.content.get_sheet(commentable, ICommentable)
        sheet.delete_field_values(['comments_count'])


@log_migration
def reindex_comments(root, registry):  # pragma: no cover
    """Update comments index."""
    from adhocracy_core.sheets.comment import ICommentable
    catalogs = find_service(root, 'catalogs')
    resources = _search_for_interfaces(catalogs, ICommentable)
    for resource in resources:
        catalogs.reindex_index(resource, 'comments')


@log_migration
def add_localroles_sheet_to_pools(root, registry):  # pragma: no cover
    """Add localroles sheet to user."""
    from adhocracy_core.sheets.localroles import ILocalRoles
    migrate_new_sheet(root, IPool, ILocalRoles)


@log_migration
def allow_image_download_view_for_everyone(root, registry):  # pragma: no cover
    """Add acls to image downloads to allow view for everyone."""
    from adhocracy_core.resources.image import IImageDownload
    from adhocracy_core.resources.image import allow_view_eveyone
    catalogs = find_service(root, 'catalogs')
    image_downloads = _search_for_interfaces(catalogs, IImageDownload)
    for image_download in image_downloads:
        allow_view_eveyone(image_download, registry, {})


@log_migration
def add_followable_sheet_to_organisation(root, registry):  # pragma: no cover
    """Add followable sheet to orgnisations."""
    migrate_new_sheet(root, IOrganisation, IFollowable)


@log_migration
def remove_participant_role_from_default_group(root,
                                               registry):  # pragma: no cover
    """Remove global participant role from default group."""
    from adhocracy_core.sheets.principal import IGroup
    groups = find_service(root, 'principals', 'groups')
    default_group = groups.get('default_group')
    group_sheet = registry.content.get_sheet(default_group, IGroup)
    appstruct = group_sheet.get()
    roles = appstruct['roles']
    if 'participant' in roles:
        roles.remove('participant')
        appstruct['roles'] = roles
        group_sheet.set(appstruct)


@log_migration
def add_activation_config_sheet_to_user(root, registry):  # pragma: no cover
    """Add acitvation configuration sheet to user."""
    from adhocracy_core.sheets.principal import IActivationConfiguration
    migrate_new_sheet(root, IUser, IActivationConfiguration)


@log_migration
def add_global_anonymous_user(root, registry):  # pragma: no cover
    """Add  global anonymmous user."""
    from pyramid.request import Request
    from adhocracy_core.resources.root import _add_anonymous_user
    from adhocracy_core.resources.principal import get_system_user_anonymous
    request = Request.blank('/dummy')
    request.registry = registry
    request.context = root
    anonymous_user = get_system_user_anonymous(request)
    if not anonymous_user:
        _add_anonymous_user(root, registry)


@log_migration
def add_allow_add_anonymized_sheet_to_process(root,
                                              registry):  # pragma: no cover
    """Add allow add anonymized sheet to process."""
    from adhocracy_core.sheets.anonymize import IAllowAddAnonymized
    migrate_new_sheet(root, IProcess, IAllowAddAnonymized)


@log_migration
def add_allow_add_anonymized_sheet_to_comments(root,
                                               registry):  # pragma: no cover
    """Add allow add anonymized sheet to comments service."""
    from adhocracy_core.sheets.anonymize import IAllowAddAnonymized
    from adhocracy_core.resources.comment import ICommentsService
    migrate_new_sheet(root, ICommentsService, IAllowAddAnonymized)


@log_migration
def add_allow_add_anonymized_sheet_to_items(root,
                                            registry):  # pragma: no cover
    """Add allow add anonymized sheet to items."""
    from adhocracy_core.sheets.anonymize import IAllowAddAnonymized
    from adhocracy_core.interfaces import IItem
    migrate_new_sheet(root, IItem, IAllowAddAnonymized)


@log_migration
def add_anonymize_default_sheet_to_user(root, registry):  # pragma: no cover
    """Add anonymize default sheet to user."""
    from adhocracy_core.sheets.principal import IAnonymizeDefault
    migrate_new_sheet(root, IUser, IAnonymizeDefault)


@log_migration
def add_allow_add_anonymized_sheet_to_rates(root,
                                            registry):  # pragma: no cover
    """Add allow add anonymized sheet to rates service."""
    from adhocracy_core.sheets.anonymize import IAllowAddAnonymized
    from adhocracy_core.resources.rate import IRatesService
    migrate_new_sheet(root, IRatesService, IAllowAddAnonymized)


@log_migration
def add_local_roles_to_acl(root, registry):  # pragma: no cover
    """Add ACE based on local roles to acl (process/organisation, proposal)."""
    from adhocracy_core.authorization import get_acl
    from adhocracy_core.authorization import _set_acl_with_local_roles
    catalogs = find_service(root, 'catalogs')
    resources = _search_for_interfaces(catalogs, IProposal)
    resources += _search_for_interfaces(catalogs, IProcess)
    resources += _search_for_interfaces(catalogs, IOrganisation)
    count = len(resources)
    for index, resource in enumerate(resources):
        logger.info('Add local roles to acl for resource {0} - {1} of {2}'
                    .format(resource, index + 1, count))
        acl = get_acl(resource)
        _set_acl_with_local_roles(resource, acl, registry)


@log_migration
def add_pages_service_to_root(root, registry):  # pragma: no cover
    """Add pages service to root."""
    from adhocracy_core.resources.page import add_page_service
    pages = find_service(root, 'pages')
    if pages is None:
        logger.info('Add pages service to {0}'.format(root))
        add_page_service(root, registry, {})


@log_migration
def add_embed_sheet_to_processes(root, registry):  # pragma: no cover
    """Add embed to processes."""
    from adhocracy_core.sheets.embed import IEmbed
    migrate_new_sheet(root, IProcess, IEmbed)


@log_migration
def reindex_users_text(root, registry):  # pragma: no cover
    """Reindex user system text index."""
    catalogs = find_service(root, 'catalogs')
    users = find_service(root, 'principals', 'users')
    for user in users.values():
        catalogs.reindex_index(user, 'text')


@log_migration
def add_activity_service_to_root(root, registry):  # pragma: no cover
    """Add activity service to root."""
    from adhocracy_core.resources.activity import add_activiy_service
    activity_stream = find_service(root, 'activity_stream')
    if activity_stream is None:
        logger.info('Add activity service to {0}'.format(root))
        add_activiy_service(root, registry, {})


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
    config.add_evolution_step(add_workflow_assignment_sheet_to_pools_simples)
    config.add_evolution_step(make_proposals_badgeable)
    config.add_evolution_step(move_sheet_annotation_data_to_attributes)
    config.add_evolution_step(migrate_rate_sheet_to_attribute_storage)
    config.add_evolution_step(move_autoname_last_counters_to_attributes)
    config.add_evolution_step(remove_empty_first_versions)
    config.add_evolution_step(make_proposalversions_polarizable)
    config.add_evolution_step(add_icanpolarize_sheet_to_comments)
    config.add_evolution_step(add_image_reference_to_users)
    config.add_evolution_step(update_asset_download_children)
    config.add_evolution_step(recreate_all_image_size_downloads)
    config.add_evolution_step(reindex_interfaces_catalog_for_root)
    config.add_evolution_step(remove_tag_resources)
    config.add_evolution_step(add_description_sheet_to_organisations)
    config.add_evolution_step(add_description_sheet_to_processes)
    config.add_evolution_step(add_image_reference_to_organisations)
    config.add_evolution_step(set_comment_count)
    config.add_evolution_step(remove_duplicated_group_ids)
    config.add_evolution_step(add_image_reference_to_proposals)
    config.add_evolution_step(reset_comment_count)
    config.add_evolution_step(remove_is_service_attribute)
    config.add_evolution_step(add_canbadge_sheet_to_users)
    config.add_evolution_step(enable_order_for_organisation)
    config.add_evolution_step(allow_create_asset_for_users)
    config.add_evolution_step(update_workflow_state_acl_for_all_resources)
    config.add_evolution_step(add_controversiality_index)
    config.add_evolution_step(add_description_sheet_to_user)
    config.add_evolution_step(set_default_workflow)
    config.add_evolution_step(add_local_roles_for_workflow_state)
    config.add_evolution_step(rename_default_group)
    config.add_evolution_step(remove_token_storage)
    config.add_evolution_step(migrate_auditlogentries_to_activities)
    config.add_evolution_step(add_notification_sheet_to_user)
    config.add_evolution_step(add_followable_sheet_to_process)
    config.add_evolution_step(add_localroles_sheet_to_pools)
    config.add_evolution_step(remove_comment_count_data)
    config.add_evolution_step(reindex_comments)
    config.add_evolution_step(allow_image_download_view_for_everyone)
    config.add_evolution_step(add_followable_sheet_to_organisation)
    config.add_evolution_step(remove_participant_role_from_default_group)
    config.add_evolution_step(add_activation_config_sheet_to_user)
    config.add_evolution_step(add_global_anonymous_user)
    config.add_evolution_step(add_allow_add_anonymized_sheet_to_process)
    config.add_evolution_step(add_allow_add_anonymized_sheet_to_comments)
    config.add_evolution_step(add_allow_add_anonymized_sheet_to_items)
    config.add_evolution_step(add_anonymize_default_sheet_to_user)
    config.add_evolution_step(add_allow_add_anonymized_sheet_to_rates)
    config.add_evolution_step(add_local_roles_to_acl)
    config.add_evolution_step(add_pages_service_to_root)
    config.add_evolution_step(add_embed_sheet_to_processes)
    config.add_evolution_step(reindex_users_text)
    config.add_evolution_step(add_activity_service_to_root)
