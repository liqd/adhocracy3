"""Alexanderplatz process resources."""

from adhocracy_core.interfaces import ITag
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import document
from adhocracy_core.resources.proposal import IGeoProposal
from adhocracy_core.resources.document_process import IDocumentProcess
from adhocracy_core.resources.document_process import document_process_meta
from adhocracy_core.resources.paragraph import IParagraph
from adhocracy_core.sheets.geo import ILocationReference
from adhocracy_core.sheets.geo import IPoint
from adhocracy_core.sheets import workflow


class IDocumentVersion(document.IDocumentVersion):

    """Versionable document with geo-location."""


document_version_meta = document.document_version_meta._replace(
    iresource=IDocumentVersion,
)._add(
    extended_sheets=(IPoint,)
)


class IDocument(document.IDocument):

    """Geolocalisable document."""


document_meta = document.document_meta._replace(
    iresource=IDocument,
    element_types=(ITag,
                   IParagraph,
                   IDocumentVersion)
)


class IProcess(IDocumentProcess):

    """Alexanderplatz participation process."""

process_meta = document_process_meta._replace(
    iresource=IProcess,
    element_types=(IGeoProposal,
                   IDocument),
    extended_sheets=(workflow.IStandard,
                     ILocationReference,)
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
    add_resource_type_to_registry(document_version_meta, config)
    add_resource_type_to_registry(document_meta, config)
