"""Reindex subscribers.

Read :mod:`substanced.catalog.subscribers` for default reindex subscribers.
"""

from pyramid.traversal import resource_path
from adhocracy_core.resources.subscriber import _add_changelog
from substanced.util import find_catalog
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.interfaces import VisibilityChange
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.interfaces import ISheetReferenceModified
from adhocracy_core.sheets.tags import ITag
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.rate import IRateable


def reindex_tagged(event):
    """Reindex tagged Itemversions subscriber."""
    # FIXME use ISheetBackReferenceModified subscriber instead
    adhocracy_catalog = find_catalog(event.object, 'adhocracy')
    old_elements_set = set(event.old_appstruct['elements'])
    new_elements_set = set(event.new_appstruct['elements'])
    newly_tagged_or_untagged_resources = old_elements_set ^ new_elements_set
    for tagged in newly_tagged_or_untagged_resources:
            adhocracy_catalog.reindex_resource(tagged)


def reindex_rate(event):
    """Reindex the rates index if a rate backreference is modified."""
    adhocracy_catalog = find_catalog(event.object, 'adhocracy')
    adhocracy_catalog.reindex_resource(event.object)


def reindex_private_visibility(event):
    """Reindex the private_visibility index for all descendants if modified."""
    visibility = _determine_visibility_change(event)
    if visibility in [VisibilityChange.concealed, VisibilityChange.revealed]:
        _reindex_resource_and_descendants(event.object)
    # TODO move changelog update to an specialised subscriber
    _add_changelog(event.registry, event.object, key='visibility',
                   value=visibility)


def _reindex_resource_and_descendants(resource: IResource):
    system_catalog = find_catalog(resource, 'system')
    if system_catalog is None:
        return  # ease testing
    adhocracy_catalog = find_catalog(resource, 'adhocracy')
    path_index = system_catalog['path']
    query = path_index.eq(resource_path(resource), include_origin=True)
    resource_and_descendants = query.execute()
    for res in resource_and_descendants:
        adhocracy_catalog.reindex_resource(res)


def _determine_visibility_change(event) -> VisibilityChange:
    is_deleted = event.new_appstruct['deleted']
    is_hidden = event.new_appstruct['hidden']
    was_deleted = event.old_appstruct['deleted']
    was_hidden = event.old_appstruct['hidden']
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
    """Register index subscribers."""
    config.add_subscriber(reindex_tagged,
                          IResourceCreatedAndAdded,
                          isheet=ITag)
    config.add_subscriber(reindex_tagged,
                          IResourceSheetModified,
                          isheet=ITag)
    config.add_subscriber(reindex_private_visibility,
                          IResourceSheetModified,
                          isheet=IMetadata)
    config.add_subscriber(reindex_rate,
                          ISheetReferenceModified,
                          isheet=IRateable)
