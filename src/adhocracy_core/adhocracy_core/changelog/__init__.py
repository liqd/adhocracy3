"""Transaction changelog for resources."""
from collections import defaultdict
from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import VisibilityChange

changelog_meta = ChangelogMetadata(modified=False,
                                   created=False,
                                   followed_by=None,
                                   resource=None,
                                   last_version=None,
                                   changed_descendants=False,
                                   changed_backrefs=False,
                                   visibility=VisibilityChange.visible,
                                   )


class Changelog(defaultdict):

    """Transaction changelog for resources.

    Dictionary with resource path as key and default value
    :class:`ChangelogMetadata`.
    """

    def __init__(self, default_factory=lambda: changelog_meta):
        super().__init__(default_factory)


def clear_changelog_callback(request):
    """Delete all entries in the transaction changelog."""
    registry = request.registry
    changelog = getattr(registry, 'changelog', {})
    changelog.clear()


def create_changelog() -> dict:
    """Return dict that maps resource path to :class:`ChangelogMetadata`."""
    metadata = lambda: changelog_meta
    return defaultdict(metadata)


def clear_modification_date_callback(request):
    """Delete the shared modification date for the transaction.

    The date is set by :func:`adhocracy_utils.get_modification_date`.
    """
    registry = request.registry
    if getattr(registry, '__modification_date__',  # pragma: no branch
               None) is not None:
        del registry.__modification_date__


def includeme(config):
    """Add transaction changelog to the registry and register subscribers."""
    config.registry.changelog = Changelog()
    config.include('.subscriber')
