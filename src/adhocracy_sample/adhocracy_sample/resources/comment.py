"""Comment resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.itemversion import itemversion_metadata
from adhocracy.resources.item import item_metadata

from adhocracy.sheets.rating import IRateable
from adhocracy_sample.sheets.comment import IComment
from adhocracy_sample.sheets.comment import ICommentable


class ICommentVersion(IItemVersion):

    """A comment in a discussion."""


commentversion_meta = itemversion_metadata._replace(
    content_name='CommentVersion',
    iresource=ICommentVersion,
    extended_sheets=[IComment,
                     ICommentable,
                     IRateable],
)


class IComment(IItem):

    """Comment versions pool."""


comment_meta = item_metadata._replace(
    content_name='Comment',
    iresource=IComment,
    element_types=[IComment,
                   ICommentVersion],
    item_type=ICommentVersion,
    use_autonaming=True,
    autonaming_prefix='comment_',
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(comment_meta, config)
    add_resource_type_to_registry(commentversion_meta, config)
