"""Comment sheet."""
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import SheetToSheet
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.sheets import GenericResourceSheet
from adhocracy.schema import ListOfUniqueReferences
from adhocracy.schema import Reference
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.schema import Text


class IComment(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the comment sheet."""


class ICommentable(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for resources that can be commented upon."""


class CommentRefersToReference(SheetToSheet):

    """Reference from comment version to the commented-on item version."""

    source_isheet = IComment
    source_isheet_field = 'refers_to'
    target_isheet = ICommentable


class CommentSchema(colander.MappingSchema):

    """Comment sheet data structure.

    `content`:  Text
    """

    refers_to = Reference(reftype=CommentRefersToReference)
    content = Text()


comment_meta = sheet_metadata_defaults._replace(isheet=IComment,
                                                schema_class=CommentSchema)


class CommentsReference(SheetToSheet):

    """Backreference for CommentRefersToReference, not stored."""

    source_isheet = ICommentable
    source_isheet_field = 'comments'
    target_isheet = IComment


class CommentableSchema(colander.MappingSchema):

    """Commentable sheet data structure.

    `comments`: list of comments (not stored)
    """

    comments = ListOfUniqueReferences(readonly=True, reftype=CommentsReference)


class CommentableSheet(GenericResourceSheet):

    """Sheet to set/get the commentable data structure."""

    isheet = ICommentable
    schema_class = CommentableSchema

    # REVIEW: instead of subclassing we could just use a special "Backref"
    # schema node type.
    def get(self):
        """Return appstruct."""
        struct = super().get()
        if self._graph:
            struct['comments'] = self._graph.get_back_reference_sources(
                self.context, CommentRefersToReference)
        return struct


commentable_meta = sheet_metadata_defaults._replace(
    isheet=ICommentable,
    schema_class=CommentableSchema,
    sheet_class=CommentableSheet,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(comment_meta, config.registry)
    add_sheet_to_registry(commentable_meta, config.registry)
