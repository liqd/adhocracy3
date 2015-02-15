"""Update transaction changelog."""
from pyramid.location import lineage
from pyramid.registry import Registry
from pyramid.traversal import find_interface, resource_path

from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.interfaces import IItemVersionNewVersionAdded
from adhocracy_core.interfaces import ISheetReferenceModified
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.utils import get_visibility_change
from adhocracy_core.sheets.metadata import IMetadata


def add_changelog_created(event):
    """Add created message to the transaction_changelog."""
    _add_changelog(event.registry, event.object, key='created', value=True)


def add_changelog_modified_and_descendants(event):
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


def add_changelog_backrefs(event):
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


def add_changelog_followed(event):
    """Add new `followed_by` and `last_version` to transaction_changelog."""
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
    changelog = registry.changelog
    path = resource_path(resource)
    metadata = changelog[path]
    old_value = getattr(metadata, key)
    if old_value is not value:
        changelog[path] = metadata._replace(**{'resource': resource,
                                               key: value})
        return True
    else:
        return False


def add_changelog_visibility(event):
    """Add new visibility message to the transaction_changelog."""
    visibility = get_visibility_change(event)
    _add_changelog(event.registry, event.object, key='visibility',
                   value=visibility)


def includeme(config):
    """Register subscriber to update transaction changelog."""
    config.add_subscriber(add_changelog_created,
                          IResourceCreatedAndAdded)
    config.add_subscriber(add_changelog_modified_and_descendants,
                          IResourceSheetModified)
    config.add_subscriber(add_changelog_backrefs,
                          ISheetReferenceModified)
    config.add_subscriber(add_changelog_followed,
                          IItemVersionNewVersionAdded)
    config.add_subscriber(add_changelog_visibility,
                          IResourceSheetModified,
                          isheet=IMetadata)
