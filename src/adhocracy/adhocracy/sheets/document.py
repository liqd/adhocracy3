"""Sheets to store a document."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import IIResourcePropertySheet
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.schema import ReferenceSetSchemaNode
from zope.interface import provider
from zope.interface import taggedValue

import colander


@provider(IIResourcePropertySheet)
class IDocument(ISheet):

    """Marker interface representing a Fubel with document data."""

    taggedValue('schema', 'adhocracy.sheets.document.DocumentSchema')


class DocumentSchema(colander.Schema):

    """Colander schema for IDocument."""

    title = colander.SchemaNode(colander.String(), default='',
                                missing=colander.drop,)
    description = colander.SchemaNode(colander.String(), default='',
                                      missing=colander.drop,)
    elements = ReferenceSetSchemaNode(
        essence_refs=True,
        default=[],
        missing=colander.drop,
        interface='adhocracy.resources.ISection')


@provider(IIResourcePropertySheet)
class ISection(ISheet):

    """Marker interface representing a document section."""

    taggedValue('schema', 'adhocracy.sheets.document.SectionSchema')


class SectionSchema(colander.Schema):

    """Colander schema for ISection."""

    title = colander.SchemaNode(colander.String(), default='',
                                missing=colander.drop,)
    elements = ReferenceSetSchemaNode(
        essence_refs=True,
        default=[],
        missing=colander.drop,
        interface='adhocracy.sheets.document.ISections')


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (IDocument, IIResourcePropertySheet),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ISection, IIResourcePropertySheet),
                                    IResourcePropertySheet)
