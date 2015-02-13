"""Transaction changelog for resources."""
from collections import defaultdict
from pyramid.registry import Registry
from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import VisibilityChange


changelog_metadata = ChangelogMetadata(False, False, None, None, None,
                                       False, False, VisibilityChange.visible)


def clear_changelog_after_commit_hook(success: bool, registry: Registry):
    """Delete all entries in the transaction changelog."""
    changelog = getattr(registry, '_transaction_changelog', dict())
    changelog.clear()


def create_changelog() -> dict:
    """Return dict that maps resource path to :class:`ChangelogMetadata`."""
    metadata = lambda: changelog_metadata
    return defaultdict(metadata)


def includeme(config):
    """Add transaction changelog to the registry and register subscribers."""
    changelog = create_changelog()
    config.registry._transaction_changelog = changelog
    config.include('.subscriber')
