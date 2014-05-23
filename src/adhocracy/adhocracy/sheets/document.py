"""Sheets to store a document."""
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import SheetToSheet
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.schema import ListOfUniqueReferences


class IDocument(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the document sheet."""


class ISection(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the section sheet."""


class IParagraph(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the paragraph sheet."""


class IDocumentElementsReference(SheetToSheet):

    """Document elements reference."""

    source_isheet = IDocument
    source_isheet_field = 'elements'
    target_isheet = ISection


class ISectionElementsReference(SheetToSheet):

    """Section element reference."""

    source_isheet = ISection
    source_isheet_field = 'elements'
    target_isheet = IParagraph


class ISubsectionsReference(SheetToSheet):

    """Section subsection reference."""

    source_isheet = ISection
    source_isheet_field = 'subsections'
    target_isheet = ISection


class DocumentSchema(colander.MappingSchema):

    """Document sheet data structure.

    `title`: one line title
    `descripton`: summary text
    `elements`: structural subelements like sections

    """

    title = colander.SchemaNode(colander.String(), default='',
                                missing=colander.drop)
    description = colander.SchemaNode(colander.String(), default='',
                                      missing=colander.drop)
    elements = ListOfUniqueReferences(reftype=IDocumentElementsReference)


document_meta = sheet_metadata_defaults._replace(isheet=IDocument,
                                                 schema_class=DocumentSchema,
                                                 )


class SectionSchema(colander.MappingSchema):

    """Section sheet data structure.

    `elements`: content subelements like paragraphs
    `subsections`: structural subelements like sections

    """

    title = colander.SchemaNode(colander.String(), default='',
                                missing=colander.drop)
    elements = ListOfUniqueReferences(reftype=ISectionElementsReference)
    subsections = ListOfUniqueReferences(reftype=ISubsectionsReference)


section_meta = sheet_metadata_defaults._replace(isheet=ISection,
                                                schema_class=SectionSchema)


class ParagraphSchema(colander.MappingSchema):

    """Section sheet data structure.

    `content`:  Text

    """

    content = colander.SchemaNode(colander.String(),
                                  default='',
                                  missing=colander.drop)


paragraph_meta = sheet_metadata_defaults._replace(isheet=IParagraph,
                                                  schema_class=ParagraphSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(document_meta, config.registry)
    add_sheet_to_registry(section_meta, config.registry)
    add_sheet_to_registry(paragraph_meta, config.registry)
