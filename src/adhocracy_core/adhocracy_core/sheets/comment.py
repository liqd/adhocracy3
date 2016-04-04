"""Comment sheet."""
from BTrees.Length import Length

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Integer
from adhocracy_core.schema import PostPool
from adhocracy_core.schema import Reference
from adhocracy_core.schema import Text
from adhocracy_core.sheets import AnnotationRessourceSheet
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


class CommentableSchema(MappingSchema):
    """Commentable sheet data structure.

    `post_pool`: Pool to post new :class:`adhocracy_sample.resource.IComment`.
    """

    comments_count = Integer(readonly=True)
    post_pool = PostPool(iresource_or_service_name='comments')


class CommentableSheet(AnnotationRessourceSheet):
    """Resource Sheet that stores data in dictionary annotation."""

    _count_field_name = 'comments_count'

    def _get_data_appstruct(self) -> dict:
        """Get data appstruct.

        `comments_count` value is converted from :class:`Btrees.Length` to int.
        """
        appstruct = super()._get_data_appstruct()
        if self._count_field_name in appstruct:
            counter = appstruct[self._count_field_name]
            appstruct[self._count_field_name] = counter.value
        return appstruct

    def _store_data(self, appstruct: dict):
        """Store data appstruct.

        `comments_count` value is converted from int to :class:`Btrees.Length`,
        to support ZODB conflict resultion.
        """
        if self._count_field_name in appstruct:
            data = getattr(self.context, self._annotation_key, {})
            if self._count_field_name not in data:
                counter = Length(0)
            else:
                counter = data[self._count_field_name]
            count = appstruct[self._count_field_name]
            counter.set(count)
            appstruct[self._count_field_name] = counter
        super()._store_data(appstruct)

commentable_meta = sheet_meta._replace(
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
