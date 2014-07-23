"""Comment sheet."""
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import SheetToSheet
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.sheets.versions import IVersionable
from adhocracy.schema import Reference
from adhocracy.schema import Text


class IComment(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the comment sheet."""


class CommentRefersToReference(SheetToSheet):

    """Reference from comment version to the commented-on item version."""

    source_isheet = IComment
    source_isheet_field = 'refers_to'
    target_isheet = IVersionable


class CommentSchema(colander.MappingSchema):

    """Section sheet data structure.

    `content`:  Text
    """

    refers_to = Reference(reftype=CommentRefersToReference)
    content = Text()


comment_meta = sheet_metadata_defaults._replace(isheet=IComment,
                                                schema_class=CommentSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(comment_meta, config.registry)
