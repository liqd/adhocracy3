"""Subscriber to track changed resources during one transaction."""
from collections import defaultdict
from collections import Sequence
from logging import getLogger

from pyramid.registry import Registry
from pyramid.traversal import resource_path
from pyramid.traversal import find_interface
from pyramid.traversal import lineage

from substanced.util import find_catalog
from substanced.util import find_service
from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.interfaces import IItemVersionNewVersionAdded
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy_core.interfaces import ISheetReferenceModified
from adhocracy_core.interfaces import VisibilityChange
from adhocracy_core.resources.principal import IGroup
from adhocracy_core.resources.principal import IUser
from adhocracy_core.sheets.principal import IPermissions
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.exceptions import AutoUpdateNoForkAllowedError
from adhocracy_core.utils import find_graph
from adhocracy_core.utils import get_following_new_version
from adhocracy_core.utils import get_last_new_version
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_iresource
from adhocracy_core.utils import get_last_version
from adhocracy_core.utils import is_batchmode
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.versions import IForkableVersionable
import adhocracy_core.sheets.tags
import adhocracy_core.sheets.rate


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


def tag_created_and_added_or_modified_subscriber(event):
    """Reindex tagged itemversions."""
    # FIXME use ISheetBackReferenceModified subscriber instead
    adhocracy_catalog = find_catalog(event.object, 'adhocracy')
    old_elements_set = set(event.old_appstruct['elements'])
    new_elements_set = set(event.new_appstruct['elements'])
    newly_tagged_or_untagged_resources = old_elements_set ^ new_elements_set
    for tagged in newly_tagged_or_untagged_resources:
            adhocracy_catalog.reindex_resource(tagged)


def rate_backreference_modified_subscriber(event):
    """Reindex the rates index if a rate backreference is modified."""
    adhocracy_catalog = find_catalog(event.object, 'adhocracy')
    adhocracy_catalog.reindex_resource(event.object)


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


def create_transaction_changelog():
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
    group = _get_default_group(event.object, event.registry)
    if group is None:  # ease testing,
        return
    _add_user_to_group(event.object, group, event.registry)


def _get_default_group(context, registry: Registry) -> IGroup:
    groups = find_service(context, 'principals', 'groups')
    default_group = groups.get('authenticated', None)
    return default_group


def _add_user_to_group(user: IUser, group: IGroup, registry: Registry):
    sheet = get_sheet(user, IPermissions)
    groups = sheet.get()['groups']
    groups.append(group)
    sheet.set({'groups': groups}, registry=registry)


def reference_has_new_version_subscriber(event):
    """Auto updated resource if a referenced Item has a new version.

    :raises AutoUpdateNoForkAllowedError: if a fork is created but not allowed
    """
    resource = event.object
    root_versions = event.root_versions
    isheet = event.isheet
    registry = event.registry
    creator = event.creator
    sheet = get_sheet(resource, isheet, registry=registry)
    autoupdate = isheet.extends(ISheetReferenceAutoUpdateMarker)
    editable = sheet.meta.editable
    graph = find_graph(resource)
    if root_versions and not graph.is_in_subtree(resource, root_versions):
        return
    if autoupdate and editable:
        appstruct = sheet.get()
        field = appstruct[event.isheet_field]
        if isinstance(field, Sequence):
            old_version_index = field.index(event.old_version)
            field.pop(old_version_index)
            field.insert(old_version_index, event.new_version)
        else:
            appstruct[event.isheet_field] = event.new_version
        if is_batchmode(registry):
            new_version = get_last_new_version(registry, resource)
        else:
            new_version = get_following_new_version(registry, resource)
        is_versionable = IVersionable.providedBy(resource)
        is_forkable = IForkableVersionable.providedBy(resource)
        # versionable without new version: create a new version store appstruct
        if is_versionable and new_version is None:
            if not is_forkable:  # pragma: no branch
                _assert_we_are_not_forking(resource, registry, event)
            _update_versionable(resource, isheet, appstruct, root_versions,
                                registry, creator)
        # versionable with new version: use new version to store appstruct
        elif is_versionable and new_version is not None:
            new_version_sheet = get_sheet(new_version, isheet,
                                          registry=registry)
            new_version_sheet.set(appstruct)
        # non versionable: store appstruct directly
        else:
            sheet.set(appstruct)


def _assert_we_are_not_forking(resource, registry, event):
    """Assert that the last tag == resource to prevent forking."""
    last = get_last_version(resource, registry)
    if last is None:
        return
    if resource is not last:
        raise AutoUpdateNoForkAllowedError(resource, event)


def _update_versionable(resource, isheet, appstruct, root_versions, registry,
                        creator) -> IResource:
    appstructs = _get_writable_appstructs(resource, registry)
    # FIXME the need to switch between forkable and non-forkable is bad
    is_forkable = IForkableVersionable.providedBy(resource)
    iversionable = IForkableVersionable if is_forkable else IVersionable
    appstructs[iversionable.__identifier__]['follows'] = [resource]
    appstructs[isheet.__identifier__] = appstruct
    iresource = get_iresource(resource)
    new_resource = registry.content.create(iresource.__identifier__,
                                           parent=resource.__parent__,
                                           appstructs=appstructs,
                                           creator=creator,
                                           registry=registry,
                                           options=root_versions)
    return new_resource


def _get_writable_appstructs(resource, registry) -> dict:
    appstructs = {}
    sheets = registry.content.get_sheets_all(resource)
    for sheet in sheets:
        editable = sheet.meta.editable
        creatable = sheet.meta.creatable
        if editable or creatable:  # pragma: no branch
            appstructs[sheet.meta.isheet.__identifier__] = sheet.get()
    return appstructs


def metadata_modified_subscriber(event):
    """Invoked after PUTting modified metadata fields.

    Reindex all resource and descendedants if hidden value is modified.
    """
    is_deleted = event.new_appstruct['deleted']
    is_hidden = event.new_appstruct['hidden']
    was_deleted = event.old_appstruct['deleted']
    was_hidden = event.old_appstruct['hidden']
    is_modified = (was_hidden != is_hidden) or (was_deleted != is_deleted)
    if is_modified:
        # reindex the private_visibility catalog index for all descendants
        _reindex_resource_and_descendants(event.object)
    visibility_change = _determine_visibility_change(was_hidden=was_hidden,
                                                     was_deleted=was_deleted,
                                                     is_hidden=is_hidden,
                                                     is_deleted=is_deleted)
    _add_changelog(event.registry, event.object, key='visibility',
                   value=visibility_change)


def _reindex_resource_and_descendants(resource: IResource):
    system_catalog = find_catalog(resource, 'system')
    adhocracy_catalog = find_catalog(resource, 'adhocracy')
    path_index = system_catalog['path']
    query = path_index.eq(resource_path(resource), include_origin=True)
    resource_and_descendants = query.execute()
    for res in resource_and_descendants:
        adhocracy_catalog.reindex_resource(res)


def _determine_visibility_change(was_hidden: bool,
                                 was_deleted: bool,
                                 is_hidden: bool,
                                 is_deleted: bool) -> VisibilityChange:
    was_visible = not (was_hidden or was_deleted)
    is_visible = not (is_hidden or is_deleted)
    if was_visible:
        if is_visible:
            return VisibilityChange.visible
        else:
            return VisibilityChange.concealed
    else:
        if is_visible:
            return VisibilityChange.revealed
        else:
            return VisibilityChange.invisible


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
    config.add_subscriber(reference_has_new_version_subscriber,
                          ISheetReferencedItemHasNewVersion,
                          isheet=ISheetReferenceAutoUpdateMarker)
    config.add_subscriber(tag_created_and_added_or_modified_subscriber,
                          IResourceCreatedAndAdded,
                          isheet=adhocracy_core.sheets.tags.ITag)
    config.add_subscriber(tag_created_and_added_or_modified_subscriber,
                          IResourceSheetModified,
                          isheet=adhocracy_core.sheets.tags.ITag)
    config.add_subscriber(user_created_and_added_subscriber,
                          IResourceCreatedAndAdded,
                          interface=IUser)
    config.add_subscriber(metadata_modified_subscriber,
                          IResourceSheetModified,
                          isheet=IMetadata)
    config.add_subscriber(rate_backreference_modified_subscriber,
                          ISheetReferenceModified,
                          isheet=adhocracy_core.sheets.rate.IRateable)
