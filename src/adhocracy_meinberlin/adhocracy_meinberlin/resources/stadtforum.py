"""Stadtforum process resources."""

"""Comment resource type."""
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.comment import ICommentVersion
from adhocracy_core.resources.comment import IComment
from adhocracy_core.resources.comment import commentversion_meta
from adhocracy_core.resources.comment import comment_meta

import adhocracy_core.sheets.comment
import adhocracy_core.sheets.rate
import adhocracy_core.sheets.polarization


class IPolarizedCommentVersion(ICommentVersion):

    """A polarized comment (pro or contra) in a discussion."""


polarizedcommentversion_meta = commentversion_meta._replace(
    content_name='PolarizedCommentVersion',
    iresource=IPolarizedCommentVersion,
    extended_sheets=(adhocracy_core.sheets.comment.IComment,
                     adhocracy_core.sheets.comment.ICommentable,
                     adhocracy_core.sheets.rate.IRateable,
                     adhocracy_core.sheets.polarization.IPolarizable,
                     ),
)


class IPolarizedComment(IComment):

    """Polarized Comment versions pool."""


polarizedcomment_meta = comment_meta._replace(
    iresource=IPolarizedComment,
    element_types=(IPolarizedCommentVersion,
                   ),
    item_type=IPolarizedCommentVersion,
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(polarizedcommentversion_meta, config)
    add_resource_type_to_registry(polarizedcomment_meta, config)
