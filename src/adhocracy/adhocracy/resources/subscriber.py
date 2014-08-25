"""Subscriber to track changed resources during one transaction."""
from collections import defaultdict

from pyramid.registry import Registry
from pyramid.traversal import resource_path

from adhocracy.interfaces import IResource, ChangelogMetadata
from adhocracy.interfaces import IResourceCreatedAndAdded
from adhocracy.interfaces import IResourceSheetModified
from adhocracy.interfaces import IItemVersionNewVersionAdded


def resource_created_and_added_subscriber(event):
    """Add created message to the transaction_changelog."""
    _add_changelog_metadata(event.registry, event.object, created=True)


def resource_modified_subscriber(event):
    """Add modified message to the transaction_changelog."""
    _add_changelog_metadata(event.registry, event.object, modified=True)


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


changelog_metadata = ChangelogMetadata(False, False, None, None)


def create_transaction_changelog():
    """Return dict that maps resource path to :class:`ChangelogMetadata`."""
    metadata = lambda: changelog_metadata
    return defaultdict(metadata)


def clear_transaction_changelog_after_commit_hook(success: bool,
                                                  registry: Registry):
    """Delete all entries in the transaction changelog."""
    changelog = getattr(registry, '_transaction_changelog', dict())
    changelog.clear()


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
