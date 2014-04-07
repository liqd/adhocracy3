"""Sheets to store a document."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import IIResourcePropertySheet
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import AdhocracyReferenceType
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.schema import ReferenceSetSchemaNode
from zope.interface import provider
from zope.interface import taggedValue

import colander


@provider(IIResourcePropertySheet)
class IDocument(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface representing an item with document data."""

    taggedValue('field:title',
                colander.SchemaNode(colander.String(),
                                    default='',
                                    missing=colander.drop,
                                    )
                )
    taggedValue('field:description',
                colander.SchemaNode(colander.String(),
                                    default='',
                                    missing=colander.drop,
                                    )
                )
    taggedValue(
        'field:elements',
        ReferenceSetSchemaNode(
            reftype='adhocracy.sheets.document.IDocumentElementsReference',
        ))


@provider(IIResourcePropertySheet)
class ISection(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface representing a document section."""

    taggedValue('field:title',
                colander.SchemaNode(colander.String(),
                                    default='',
                                    missing=colander.drop,
                                    )
                )
    taggedValue(
        'field:elements',
        ReferenceSetSchemaNode(
            reftype='adhocracy.sheets.document.ISectionElementsReference',
        ))
    taggedValue(
        'field:subsections',
        ReferenceSetSchemaNode(
            reftype='adhocracy.sheets.document.ISubsectionsReference',
        ))


@provider(IIResourcePropertySheet)
class IParagraph(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface representing a document paragraph."""

    taggedValue('field:content',
                colander.SchemaNode(colander.String(),
                                    default='',
                                    missing=colander.drop,
                                    )
                )


class IDocumentElementsReference(AdhocracyReferenceType):

    """IDocument reference."""

    source_isheet = IDocument
    source_isheet_field = 'elements'
    target_isheet = ISection


class ISectionElementsReference(AdhocracyReferenceType):

    """Reference from a section to its direct elements, such as paragraphs."""

    source_isheet = ISection
    source_isheet_field = 'elements'
    target_isheet = IParagraph


class ISubsectionsReference(AdhocracyReferenceType):

    """Reference from a section to its subsections."""

    source_isheet = ISection
    source_isheet_field = 'subsections'
    target_isheet = ISection


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (IDocument, IIResourcePropertySheet),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ISection, IIResourcePropertySheet),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (IParagraph, IIResourcePropertySheet),
                                    IResourcePropertySheet)
