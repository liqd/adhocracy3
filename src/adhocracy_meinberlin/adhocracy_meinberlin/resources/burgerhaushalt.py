"""Burgerhaushalt proposal."""
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal
from adhocracy_core.sheets.geo import IPoint
from adhocracy_core.sheets.geo import ILocationReference
from adhocracy_core.sheets.image import IImageReference
import adhocracy_meinberlin.sheets.burgerhaushalt


class IProposalVersion(proposal.IProposalVersion):
    """Burgerhaushalt proposal version."""


proposal_version_meta = proposal.proposal_version_meta._replace(
    iresource=IProposalVersion,
)._add(extended_sheets=(adhocracy_meinberlin.sheets.burgerhaushalt.IProposal,
                        IPoint))


class IProposal(proposal.IProposal):
    """Burgerhaushalt proposal versions pool."""


proposal_meta = proposal.proposal_meta._replace(
    iresource=IProposal,
    element_types=(IProposalVersion,),
    item_type=IProposalVersion,
)


class IProcess(process.IProcess):
    """Burgerhaushalt participation process."""


process_meta = process.process_meta._replace(
    content_name='BuergerhaushaltProcess',
    iresource=IProcess,
    element_types=(IProposal,
                   ),
    is_implicit_addable=True,
    extended_sheets=(
        ILocationReference,
        IImageReference,
    ),
    default_workflow='standard',
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(proposal_version_meta, config)
    add_resource_type_to_registry(process_meta, config)
