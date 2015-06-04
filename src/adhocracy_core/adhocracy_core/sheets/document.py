"""Sheets to store a document."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.schema import Text
from adhocracy_core.schema import SingleLine


class IDocument(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the document sheet."""


class ISection(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the section sheet."""


class IParagraph(ISection):

    """Marker interface for the paragraph sheet."""


class DocumentElementsReference(SheetToSheet):

    """Document elements reference."""

    source_isheet = IDocument
    source_isheet_field = 'elements'
    target_isheet = ISection


class DocumentSchema(colander.MappingSchema):

    """Document sheet data structure.

    `title`: one line title
    `description`: summary text
    `elements`: structural subelements like sections
    """

    title = SingleLine()
    description = Text()
    elements = UniqueReferences(reftype=DocumentElementsReference)


document_meta = sheet_meta._replace(isheet=IDocument,
                                    schema_class=DocumentSchema,
                                    )


class ParagraphSchema(colander.MappingSchema):

    """Paragraph Section sheet data structure.

    `content`:  Text
    `documents`: Documents referencing this paragraph
    """

    text = Text()
    documents = UniqueReferences(reftype=DocumentElementsReference,
                                 readonly=True,
                                 backref=True)


paragraph_meta = sheet_meta._replace(isheet=IParagraph,
                                     schema_class=ParagraphSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(document_meta, config.registry)
    add_sheet_to_registry(paragraph_meta, config.registry)
