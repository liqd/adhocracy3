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
    taggedValue('field:elements',
                ReferenceSetSchemaNode(
                    default=[],
                    missing=colander.drop,
                    interfaces=
                    ['adhocracy.sheets.document.ISection'],
                )
                )


@provider(IIResourcePropertySheet)
class ISection(ISheet):

    """Marker interface representing a document section."""

    taggedValue('field:title',
                colander.SchemaNode(colander.String(),
                                    default='',
                                    missing=colander.drop,
                                    )
                )
    taggedValue('field:elements',
                ReferenceSetSchemaNode(
                    default=[],
                    missing=colander.drop,
                    interfaces=
                    ['adhocracy.sheets.document.ISection'],
                )
                )


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (IDocument, IIResourcePropertySheet),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ISection, IIResourcePropertySheet),
                                    IResourcePropertySheet)
