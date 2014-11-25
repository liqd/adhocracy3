"""Subscriber to track changed resources during one transaction."""
from collections import defaultdict
from collections import Sequence
from logging import getLogger

from pyramid.registry import Registry
from pyramid.traversal import resource_path
from substanced.util import find_catalog
from substanced.util import find_service

from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItemVersionNewVersionAdded
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy_core.interfaces import ISheetReferenceModified
from adhocracy_core.resources.principal import IGroup
from adhocracy_core.resources.principal import IUser
from adhocracy_core.sheets.principal import IPermissions
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.utils import find_graph
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_iresource
from adhocracy_core.utils import raise_colander_style_error

import adhocracy_core.sheets.versions
import adhocracy_core.sheets.tags
import adhocracy_core.sheets.rate


changelog_metadata = ChangelogMetadata(False, False, None, None)
logger = getLogger(__name__)


def resource_created_and_added_subscriber(event):
    """Add created message to the transaction_changelog."""
    _add_changelog_metadata(event.registry, event.object, created=True)


def resource_modified_subscriber(event):
    """Add modified message to the transaction_changelog."""
    _add_changelog_metadata(event.registry, event.object, modified=True)


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
    """Add new follwed_by version to the transaction_changelog."""
    if event.new_version is None:
        return
    _add_changelog_metadata(event.registry, event.object,
                            followed_by=event.new_version)


def _add_changelog_metadata(registry: Registry, resource: IResource, **kwargs):
    """Add changelog metadata `kwargs` to the transaction changelog."""
    changelog = registry._transaction_changelog
    path = resource_path(resource)
    metadata = changelog[path]
    changelog[path] = metadata._replace(resource=resource, **kwargs)


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
    """Auto updated resource if a referenced Item has a new version."""
    resource = event.object
    root_versions = event.root_versions
    isheet = event.isheet
    registry = event.registry
    creator = event.creator
    sheet = get_sheet(resource, isheet, registry=registry)
    autoupdate = isheet.extends(ISheetReferenceAutoUpdateMarker)
    editable = sheet.meta.editable

    if autoupdate and editable:
        appstruct = sheet.get()
        field = appstruct[event.isheet_field]
        if isinstance(field, Sequence):
            old_version_index = field.index(event.old_version)
            field.pop(old_version_index)
            field.insert(old_version_index, event.new_version)
        else:
            appstruct[event.isheet_field] = event.new_version
        new_version = _get_new_version_created_in_this_transaction(registry,
                                                                   resource)
        if IItemVersion.providedBy(resource) and new_version is None:
            _update_versionable(resource, isheet, appstruct, root_versions,
                                registry, creator)
        else:
            sheet.set(appstruct)


def _get_new_version_created_in_this_transaction(registry,
                                                 resource) -> IResource:
        if not hasattr(registry, '_transaction_changelog'):
            return
        path = resource_path(resource)
        changelog_metadata = registry._transaction_changelog[path]
        return changelog_metadata.followed_by


def _update_versionable(resource, isheet, appstruct, root_versions, registry,
                        creator) -> IResource:
    graph = find_graph(resource)
    if root_versions and not graph.is_in_subtree(resource, root_versions):
        return resource
    else:
        appstructs = _get_writable_appstructs(resource, registry)
        versionable_sheet = adhocracy_core.sheets.versions.IVersionable
        appstructs[versionable_sheet.__identifier__]['follows'] = [resource]
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
    """Invoked after PUTting modified metadata fields."""
    is_deleted = event.new_appstruct['deleted']
    is_hidden = event.new_appstruct['hidden']
    was_deleted = event.old_appstruct['deleted']
    was_hidden = event.old_appstruct['hidden']

    if was_hidden != is_hidden:
        if event.request is None:
            logger.warning('Ignoring request to change hidden status to %s '
                           'since we cannot check permissions',
                           is_hidden)
            return
        if not event.request.has_permission('hide_resource', event.object):
            raise_colander_style_error(IMetadata,
                                       'hidden',
                                       'Changing this field is not allowed')

    # Store hidden/deleted status in object for efficient access
    event.object.deleted = is_deleted
    event.object.hidden = is_hidden

    if (was_hidden != is_hidden) or (was_deleted != is_deleted):
        _reindex_resource_and_descendants(event.object)


def _reindex_resource_and_descendants(resource: IResource):
    system_catalog = find_catalog(resource, 'system')
    adhocracy_catalog = find_catalog(resource, 'adhocracy')
    path_index = system_catalog['path']
    query = path_index.eq(resource_path(resource), include_origin=True)
    resource_and_descendants = query.execute()
    for res in resource_and_descendants:
        adhocracy_catalog.reindex_resource(res)


def includeme(config):
    """Add transaction changelog to the registry and register subscribers."""
    changelog = create_transaction_changelog()
    config.registry._transaction_changelog = changelog
    config.add_subscriber(resource_created_and_added_subscriber,
                          IResourceCreatedAndAdded)
    config.add_subscriber(resource_modified_subscriber,
                          IResourceSheetModified)
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
