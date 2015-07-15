"""Alexanderplatz process resources."""

from adhocracy_core.interfaces import ITag
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import document
from adhocracy_core.resources import proposal
from adhocracy_core.resources.document_process import IDocumentProcess
from adhocracy_core.resources.document_process import document_process_meta
from adhocracy_core.resources.paragraph import IParagraph
from adhocracy_core.sheets.geo import ILocationReference
from adhocracy_core.sheets.geo import IPoint


class IProposalVersion(proposal.IProposalVersion):

    """Alexanderplatz proposal version."""


proposal_version_meta = proposal.proposal_version_meta._replace(
    iresource=IProposalVersion,
)._add(extended_sheets=(IPoint,))


class IProposal(proposal.IProposal):

    """Alexanderplatz proposal versions pool."""

proposal_meta = proposal.proposal_meta._replace(
    iresource=IProposal,
    element_types=(IProposalVersion,),
    item_type=IProposalVersion,
)


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
    element_types=(IProposal,
                   IDocument)
)._add(extended_sheets=(ILocationReference,))


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(proposal_version_meta, config)
    add_resource_type_to_registry(process_meta, config)
    add_resource_type_to_registry(document_version_meta, config)
    add_resource_type_to_registry(document_meta, config)
