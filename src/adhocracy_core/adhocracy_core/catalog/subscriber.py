"""Reindex subscribers.

Read :mod:`substanced.catalog.subscribers` for default reindex subscribers.
"""

from substanced.util import find_catalog

from adhocracy_core.utils import get_visibility_change
from adhocracy_core.interfaces import VisibilityChange
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.interfaces import ISheetBackReferenceModified
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.utils import list_resource_with_descendants


def reindex_tag(event):
    """Reindex tag index if a tag backreference is modified."""
    # TODO: als long as we cannot reindex a single index this function
    # does the same like reindex_rate: reindex all indexes
    adhocracy_catalog = find_catalog(event.object, 'adhocracy')
    adhocracy_catalog.reindex_resource(event.object)


def reindex_rate(event):
    """Reindex the rates index if a rate backreference is modified."""
    adhocracy_catalog = find_catalog(event.object, 'adhocracy')
    adhocracy_catalog.reindex_resource(event.object)


def reindex_visibility(event):
    """Reindex the private_visibility index for all descendants if modified."""
    visibility = get_visibility_change(event)
    if visibility in (VisibilityChange.concealed, VisibilityChange.revealed):
        _reindex_resource_and_descendants(event.object)


def _reindex_resource_and_descendants(resource: IResource):
    adhocracy_catalog = find_catalog(resource, 'adhocracy')
    if adhocracy_catalog is None:
        return  # ease testing
    resource_and_descendants = list_resource_with_descendants(resource)
    for res in resource_and_descendants:
        adhocracy_catalog.reindex_resource(res)


def includeme(config):
    """Register index subscribers."""
    config.add_subscriber(reindex_tag,
                          ISheetBackReferenceModified,
                          object_iface=IVersionable)
    config.add_subscriber(reindex_visibility,
                          IResourceSheetModified,
                          event_isheet=IMetadata)
    config.add_subscriber(reindex_rate,
                          ISheetBackReferenceModified,
                          event_isheet=IRateable)
