"""Alexanderplatz process resources."""

from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.proposal import IGeoProposal
from adhocracy_core.resources import proposal
from adhocracy_core.resources.document import IGeoDocument
from adhocracy_core.resources.document_process import IDocumentProcess
from adhocracy_core.resources.document_process import document_process_meta
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


class IProcess(IDocumentProcess):

    """Alexanderplatz participation process."""

process_meta = document_process_meta._replace(
    iresource=IProcess,
    element_types=(IGeoProposal,
                   IGeoDocument),
    extended_sheets=(ILocationReference,
                     ),
    workflow_name='standard',
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
