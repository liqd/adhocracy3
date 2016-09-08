"""Comment sheet."""

from colander import deferred
from substanced.util import find_service
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Integer
from adhocracy_core.schema import PostPool
from adhocracy_core.schema import Reference
from adhocracy_core.schema import Text
from adhocracy_core.sheets import sheet_meta


class IComment(ISheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for the comment sheet."""


class ICommentable(ISheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for resources that can be commented upon."""


class CommentRefersToReference(SheetToSheet):
    """Reference from comment version to the commented-on item version."""

    source_isheet = IComment
    source_isheet_field = 'refers_to'
    target_isheet = ICommentable


class CommentSchema(MappingSchema):
    """Comment sheet data structure.

    `content`:  Text
    """

    refers_to = Reference(reftype=CommentRefersToReference)
    content = Text()
    # TODO add post_pool validator


comment_meta = sheet_meta._replace(isheet=IComment,
                                   schema_class=CommentSchema)


@deferred
def deferred_default_comment_count(node: MappingSchema, kw: dict) -> str:
    """Return comment_count of the current `context` resource."""
    context = kw['context']
    catalogs = find_service(context, 'catalogs')
    return catalogs.get_index_value(context, 'comments')


class CommentableSchema(MappingSchema):
    """Commentable sheet data structure.

    `post_pool`: Pool to post new :class:`adhocracy_sample.resource.IComment`.
    """

    comments_count = Integer(readonly=True,
                             default=deferred_default_comment_count)
    post_pool = PostPool(iresource_or_service_name='comments')


commentable_meta = sheet_meta._replace(
    isheet=ICommentable,
    schema_class=CommentableSchema,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(comment_meta, config.registry)
    add_sheet_to_registry(commentable_meta, config.registry)
