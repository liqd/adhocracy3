"""Comment resource type."""
from pyramid.registry import Registry

from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_meta
from adhocracy_core.resources.item import item_meta
from adhocracy_core.resources.service import service_meta

import adhocracy_core.sheets.comment
import adhocracy_core.sheets.rate


class ICommentVersion(IItemVersion):

    """A comment in a discussion."""


commentversion_meta = itemversion_meta._replace(
    content_name='CommentVersion',
    iresource=ICommentVersion,
    extended_sheets=[adhocracy_core.sheets.comment.IComment,
                     adhocracy_core.sheets.comment.ICommentable,
                     adhocracy_core.sheets.rate.IRateable],
    permission_create='edit_comment',
)


class IComment(IItem):

    """Comment versions pool."""


comment_meta = item_meta._replace(
    content_name='Comment',
    iresource=IComment,
    element_types=[ICommentVersion,
                   ],
    item_type=ICommentVersion,
    use_autonaming=True,
    autonaming_prefix='comment_',
    permission_create='create_comment',
)


class ICommentsService(IServicePool):

    """The 'comments' ServicePool."""


comments_meta = service_meta._replace(
    iresource=ICommentsService,
    content_name='comments',
    element_types=[IComment],
)


def add_commentsservice(context: IPool, registry: Registry, options: dict):
    """Add `comments` service to context."""
    registry.content.create(ICommentsService.__identifier__, parent=context)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(comments_meta, config)
    add_resource_type_to_registry(commentversion_meta, config)
    add_resource_type_to_registry(comment_meta, config)
