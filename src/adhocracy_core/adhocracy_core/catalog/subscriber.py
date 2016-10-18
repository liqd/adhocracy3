"""Reindex subscribers.

Read :mod:`substanced.catalog.subscribers` for default reindex subscribers.
"""

from pyramid.traversal import get_current_registry
from substanced.util import find_service

from adhocracy_core.utils import get_visibility_change
from adhocracy_core.interfaces import VisibilityChange
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.interfaces import ISheetBackReferenceModified
from adhocracy_core.interfaces import ISheetBackReferenceRemoved
from adhocracy_core.interfaces import IItem
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.comment import IComment
from adhocracy_core.sheets.comment import ICommentable
from adhocracy_core.sheets.badge import IBadgeAssignment
from adhocracy_core.sheets.badge import IBadgeable
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.utils import list_resource_with_descendants


def reindex_tag(event):
    """Reindex tag index if a tag backreference is modified."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'tag')


def reindex_rates(event):
    """Reindex the rates index if a rate backreference is modified."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'rates')


def reindex_controversiality(event):
    """Reindex the controversiality index if backreference is modified."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'controversiality')


def reindex_user_name(event):
    """Reindex indexes `user_name`."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'user_name')


def reindex_user_email(event):
    """Reindex indexes `private_user_email`."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'private_user_email')


def reindex_user_activation_path(event):
    """Reindex indexes `private_user_activation_path`."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'private_user_activation_path')


def reindex_badge(event):
    """Reindex badge index if a backreference is modified/created."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'badge')


def reindex_visibility(event):
    """Reindex the private_visibility index for all descendants if modified."""
    visibility = get_visibility_change(event)
    if visibility in (VisibilityChange.concealed, VisibilityChange.revealed):
        _reindex_resource_and_descendants(event.object)


def _reindex_resource_and_descendants(resource: IResource):
    catalogs = find_service(resource, 'catalogs')
    if catalogs is None:  # ease testing
        return
    resource_and_descendants = list_resource_with_descendants(resource)
    for res in resource_and_descendants:
        catalogs.reindex_index(res, 'private_visibility')


def reindex_item_badge(event):
    """Reindex `item_badge` for all item versions of èvent.object."""
    catalogs = find_service(event.object, 'catalogs')
    children = event.object.values()
    versionables = (c for c in children if IVersionable.providedBy(c))
    for versionable in versionables:
        catalogs.reindex_index(versionable, 'item_badge')


def reindex_workflow_state(event):
    """Reindex the workflow_state index for item and its versions."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'workflow_state')
    children = event.object.values()
    versionables = (c for c in children if IVersionable.providedBy(c))
    for versionable in versionables:
        catalogs.reindex_index(versionable, 'workflow_state')


def reindex_comments(event):
    """Reindex comments index if a backreference is modified/created."""
    catalogs = find_service(event.object, 'catalogs')
    commentables = _get_affected_commentables(event.object)
    for commentable in commentables:
        catalogs.reindex_index(commentable, 'comments')


def _get_affected_commentables(commentable):
    registry = get_current_registry(commentable)
    commentables = [commentable]
    while IComment.providedBy(commentable):
        commentable = registry.content.get_sheet_field(commentable, IComment,
                                                       'refers_to')
        if commentable:
            commentables.append(commentable)
    return commentables


def reindex_user_text(event):
    """Reindex indexes `text`."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'text')


def includeme(config):
    """Register index subscribers."""
    config.add_subscriber(reindex_tag,
                          ISheetBackReferenceModified,
                          object_iface=IVersionable)
    config.add_subscriber(reindex_visibility,
                          IResourceSheetModified,
                          event_isheet=IMetadata)
    config.add_subscriber(reindex_rates,
                          ISheetBackReferenceModified,
                          event_isheet=IRateable)
    config.add_subscriber(reindex_controversiality,
                          ISheetBackReferenceModified,
                          event_isheet=IRateable)
    config.add_subscriber(reindex_controversiality,
                          ISheetBackReferenceModified,
                          event_isheet=ICommentable)
    config.add_subscriber(reindex_badge,
                          ISheetBackReferenceModified,
                          event_isheet=IBadgeable)
    config.add_subscriber(reindex_badge,
                          ISheetBackReferenceRemoved,
                          event_isheet=IBadgeAssignment)
    config.add_subscriber(reindex_item_badge,
                          ISheetBackReferenceModified,
                          object_iface=IItem,
                          event_isheet=IBadgeable)
    config.add_subscriber(reindex_workflow_state,
                          IResourceSheetModified,
                          event_isheet=IWorkflowAssignment)
    config.add_subscriber(reindex_user_name,
                          IResourceSheetModified,
                          event_isheet=IUserBasic)
    config.add_subscriber(reindex_user_email,
                          IResourceSheetModified,
                          event_isheet=IUserExtended)
    config.add_subscriber(reindex_user_activation_path,
                          IResourceSheetModified,
                          event_isheet=IUserBasic)
    config.add_subscriber(reindex_comments,
                          ISheetBackReferenceModified,
                          event_isheet=ICommentable)
    config.add_subscriber(reindex_user_text,
                          IResourceSheetModified,
                          event_isheet=IUserBasic)
    config.add_subscriber(reindex_user_text,
                          IResourceSheetModified,
                          event_isheet=IUserExtended)
    # add subscriber to updated allowed index
    config.scan('substanced.objectmap.subscribers')
