"""Sheets to store a document."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.schema import ReferenceSetSchemaNode
from zope.interface import provider
from zope.interface import taggedValue
from zope.interface.interfaces import IInterface

import colander


@provider(IISheet)
class IDocument(ISheet):

    """Marker interface representing a Fubel with document data."""

    taggedValue('schema', 'adhocracy.sheets.document.DocumentSchema')


class DocumentSchema(colander.Schema):

    """Colander schema for IDocument."""

    elements = ReferenceSetSchemaNode(
        essence_refs=True,
        default=[],
        missing=colander.drop,
        interface='adhocracy.resources.ISection')


@provider(IISheet)
class ISection(ISheet):

    """Marker interface representing a document section."""

    taggedValue('schema', 'adhocracy.sheets.document.SectionSchema')


class SectionSchema(colander.Schema):

    """Colander schema for ISection."""

    title = colander.SchemaNode(colander.String(), default='')
    elements = ReferenceSetSchemaNode(
        essence_refs=True,
        default=[],
        missing=colander.drop,
        interface='adhocracy.sheets.document.ISections')


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (IDocument, IInterface),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ISection, IInterface),
                                    IResourcePropertySheet)
