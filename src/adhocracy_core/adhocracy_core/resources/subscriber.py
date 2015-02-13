"""Autoupdate resources."""
# TODO move changelog subscribers to different package

from collections import defaultdict
from collections import Sequence
from logging import getLogger

from pyramid.registry import Registry
from pyramid.traversal import resource_path
from pyramid.traversal import find_interface
from pyramid.traversal import lineage

from substanced.util import find_service
from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import ISimple
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.interfaces import IItemVersionNewVersionAdded
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import ISheetReferenceNewVersion
from adhocracy_core.interfaces import ISheetReferenceModified
from adhocracy_core.interfaces import VisibilityChange
from adhocracy_core.resources.principal import IGroup
from adhocracy_core.resources.principal import IUser
from adhocracy_core.sheets.principal import IPermissions
from adhocracy_core.exceptions import AutoUpdateNoForkAllowedError
from adhocracy_core.utils import find_graph
from adhocracy_core.utils import get_following_new_version
from adhocracy_core.utils import get_last_new_version
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.utils import get_iresource
from adhocracy_core.utils import get_last_version
from adhocracy_core.sheets.versions import IVersionable


changelog_metadata = ChangelogMetadata(False, False, None, None, None,
                                       False, False, VisibilityChange.visible)
logger = getLogger(__name__)


def resource_created_and_added_subscriber(event):
    """Add created message to the transaction_changelog."""
    _add_changelog(event.registry, event.object, key='created', value=True)


def resource_modified_subscriber(event):
    """Add modified message to the transaction_changelog."""
    _add_changelog(event.registry, event.object, key='modified', value=True)
    _add_changed_descendants_to_all_parents(event.registry, event.object)


def _add_changed_descendants_to_all_parents(registry, resource):
    for parent in lineage(resource.__parent__):
        changed_descendants_is_changed = _add_changelog(
            registry, parent, key='changed_descendants', value=True)
        if changed_descendants_is_changed:
            _increment_changed_descendants_counter(parent)
        else:
            break


def _increment_changed_descendants_counter(context):
    counter = getattr(context, '__changed_descendants_counter__', None)
    if counter is not None:  # pragma: no branch
        counter.change(1)


def resource_backreference_modified_subscriber(event):
    """Add changed_backrefs message to the transaction_changelog."""
    changed_backrefs_is_modified = _add_changelog(event.registry, event.object,
                                                  key='changed_backrefs',
                                                  value=True)
    if changed_backrefs_is_modified:
        _increment_changed_backrefs_counter(event.object)
    _add_changed_descendants_to_all_parents(event.registry, event.object)


def _increment_changed_backrefs_counter(context):
    counter = getattr(context, '__changed_backrefs_counter__', None)
    if counter is not None:  # pragma: no branch
        counter.change(1)


def itemversion_created_subscriber(event):
    """Add new `follwed_by` and `last_version` to the transaction_changelog."""
    if event.new_version is None:
        return
    _add_changelog(event.registry, event.object, key='followed_by',
                   value=event.new_version)
    item = find_interface(event.object, IItem)
    _add_changelog(event.registry, item, key='last_version',
                   value=event.new_version)


def _add_changelog(registry: Registry, resource: IResource, key: str,
                   value: object) -> bool:
    """Add metadata `key/value` to the transaction changelog if needed.

    Return: True if new metadata value was added else False (no value change)
    """
    changelog = registry._transaction_changelog
    path = resource_path(resource)
    metadata = changelog[path]
    old_value = getattr(metadata, key)
    if old_value is not value:
        changelog[path] = metadata._replace(**{'resource': resource,
                                               key: value})
        return True
    else:
        return False


def create_transaction_changelog() -> dict:
    """Return dict that maps resource path to :class:`ChangelogMetadata`."""
    metadata = lambda: changelog_metadata
    return defaultdict(metadata)


def clear_transaction_changelog_after_commit_hook(success: bool,
                                                  registry: Registry):
    """Delete all entries in the transaction changelog."""
    changelog = getattr(registry, '_transaction_changelog', dict())
    changelog.clear()


def user_created_and_added_subscriber(event):
    """Add default group to user."""
    group = _get_default_group(event.object)
    if group is None:  # ease testing,
        return
    _add_user_to_group(event.object, group, event.registry)


def _get_default_group(context) -> IGroup:
    groups = find_service(context, 'principals', 'groups')
    if groups is None:  # ease testing
        return
    default_group = groups.get('authenticated', None)
    return default_group


def _add_user_to_group(user: IUser, group: IGroup, registry: Registry):
    sheet = get_sheet(user, IPermissions)
    groups = sheet.get()['groups']
    groups.append(group)
    sheet.set({'groups': groups}, registry=registry)


def autoupdate_versionable_has_new_version(event):
    """Auto updated versionable resource if a reference has new version.

    :raises AutoUpdateNoForkAllowedError: if a fork is created but not allowed
    """
    if not _is_in_root_version_subtree(event):
        return
    sheet = get_sheet(event.object, event.isheet, event.registry)
    if not sheet.meta.editable:
        return
    appstruct = _get_updated_appstruct(event, sheet)
    new_version = _get_last_version_created_in_transaction(event)
    if new_version is None:
        if _new_version_needed_and_not_forking(event):
            _create_new_version(event, appstruct)
    else:
        new_version_sheet = get_sheet(new_version, event.isheet,
                                      event.registry)
        new_version_sheet.set(appstruct)


def _is_in_root_version_subtree(event: ISheetReferenceNewVersion) -> bool:
    if event.root_versions == []:
        return True
    graph = find_graph(event.object)
    return graph.is_in_subtree(event.object, event.root_versions)


def _get_updated_appstruct(event: ISheetReferenceNewVersion,
                           sheet: ISheet) -> dict:
    appstruct = sheet.get()
    field = appstruct[event.isheet_field]
    if isinstance(field, Sequence):
        old_version_index = field.index(event.old_version)
        field.pop(old_version_index)
        field.insert(old_version_index, event.new_version)
    else:
        appstruct[event.isheet_field] = event.new_version
    return appstruct


def _get_last_version_created_in_transaction(event: ISheetReferenceNewVersion)\
        -> IItemVersion:
    if event.is_batchmode:
        new_version = get_last_new_version(event.registry, event.object)
    else:
        new_version = get_following_new_version(event.registry, event.object)
    return new_version


def _new_version_needed_and_not_forking(event: ISheetReferenceNewVersion)\
        -> bool:
    """Check whether to autoupdate if resource is non-forkable.

    If the given resource is the last version or there's no last version yet,
    do autoupdate.

    If it's not the last version, but references the same object (namely the
    one which caused the autoupdate), don't update.

    If it's not the last version, but references a different object,
    throw an AutoUpdateNoForkAllowedError. This should only happen in batch
    requests.
    """
    last = get_last_version(event.object, event.registry)
    if last is None or last is event.object:
        return True
    value = get_sheet_field(event.object, event.isheet, event.isheet_field,
                            event.registry)
    last_value = get_sheet_field(last, event.isheet, event.isheet_field,
                                 event.registry)
    if last_value == value:
        return False
    else:
        raise AutoUpdateNoForkAllowedError(event.object, event)


def _create_new_version(event, appstruct) -> IResource:
    appstructs = _get_writable_appstructs(event.object, event.registry)
    appstructs[IVersionable.__identifier__]['follows'] = [event.object]
    appstructs[event.isheet.__identifier__] = appstruct
    registry = event.registry
    iresource = get_iresource(event.object)
    new_version = registry.content.create(iresource.__identifier__,
                                          parent=event.object.__parent__,
                                          appstructs=appstructs,
                                          creator=event.creator,
                                          registry=event.registry,
                                          root_versions=event.root_versions,
                                          is_batchmode=event.is_batchmode,
                                          )
    return new_version


def _get_writable_appstructs(resource, registry) -> dict:
    appstructs = {}
    sheets = registry.content.get_sheets_all(resource)
    for sheet in sheets:
        editable = sheet.meta.editable
        creatable = sheet.meta.creatable
        if editable or creatable:  # pragma: no branch
            appstructs[sheet.meta.isheet.__identifier__] = sheet.get()
    return appstructs


def autoupdate_non_versionable_has_new_version(event):
    """Auto update non versionable resources if a reference has new version."""
    if not _is_in_root_version_subtree(event):
        return
    sheet = get_sheet(event.object, event.isheet, event.registry)
    if not sheet.meta.editable:
        return
    appstruct = _get_updated_appstruct(event, sheet)
    sheet.set(appstruct)


def includeme(config):
    """Add transaction changelog to the registry and register subscribers."""
    changelog = create_transaction_changelog()
    config.registry._transaction_changelog = changelog
    config.add_subscriber(resource_created_and_added_subscriber,
                          IResourceCreatedAndAdded)
    config.add_subscriber(resource_modified_subscriber,
                          IResourceSheetModified)
    config.add_subscriber(resource_backreference_modified_subscriber,
                          ISheetReferenceModified)
    config.add_subscriber(itemversion_created_subscriber,
                          IItemVersionNewVersionAdded)
    config.add_subscriber(autoupdate_versionable_has_new_version,
                          ISheetReferenceNewVersion,
                          interface=IItemVersion,
                          isheet=ISheetReferenceAutoUpdateMarker)
    config.add_subscriber(autoupdate_non_versionable_has_new_version,
                          ISheetReferenceNewVersion,
                          interface=IPool,
                          isheet=ISheetReferenceAutoUpdateMarker)
    config.add_subscriber(autoupdate_non_versionable_has_new_version,
                          ISheetReferenceNewVersion,
                          interface=ISimple,
                          isheet=ISheetReferenceAutoUpdateMarker)
    config.add_subscriber(user_created_and_added_subscriber,
                          IResourceCreatedAndAdded,
                          interface=IUser)
