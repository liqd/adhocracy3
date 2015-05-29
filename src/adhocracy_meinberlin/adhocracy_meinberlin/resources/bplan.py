"""BPlan process resources."""
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_meta
from adhocracy_core.resources.item import item_meta
from adhocracy_core.resources import process
import adhocracy_meinberlin.sheets.bplan


class IProposalVersion(IItemVersion):

    """BPlan proposal version."""


proposal_version_meta = itemversion_meta._replace(
    content_name='ProposalVersion',
    iresource=IProposalVersion,
    extended_sheets=[adhocracy_meinberlin.sheets.bplan.IProposal,
                     ],
    permission_create='edit_proposal',
)


class IProposal(IItem):

    """BPlan proposal versions pool."""


proposal_meta = item_meta._replace(
    content_name='Proposal',
    iresource=IProposal,
    element_types=[IProposalVersion],
    item_type=IProposalVersion,
    is_implicit_addable=True,
    permission_create='create_proposal',
    extended_sheets=[
        adhocracy_meinberlin.sheets.bplan.IPrivateWorkflowAssignment],
)


class IProcess(process.IProcess):

    """BPlan participation process."""


process_meta = process.process_meta._replace(
    iresource=IProcess,
    element_types=[IProposal,
                   ],
    is_implicit_addable=True,
    extended_sheets=[adhocracy_meinberlin.sheets.bplan.IWorkflowAssignment,
                     ],
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(proposal_version_meta, config)
    add_resource_type_to_registry(process_meta, config)
