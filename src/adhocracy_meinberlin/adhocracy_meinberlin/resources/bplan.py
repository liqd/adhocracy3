"""BPlan process resources."""
from pyramid.interfaces import IRequest
from adhocracy_core.interfaces import IResource
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal
from adhocracy_core.sheets.embed import embed_code_config_adapter
from adhocracy_core.sheets.embed import IEmbedCodeConfig
import adhocracy_meinberlin.sheets.bplan
import adhocracy_core.sheets.image


class IProposalVersion(proposal.IProposalVersion):
    """BPlan proposal version."""


proposal_version_meta = proposal.proposal_version_meta._replace(
    content_name='ProposalVersion',
    iresource=IProposalVersion,
    extended_sheets=(adhocracy_meinberlin.sheets.bplan.IProposal,
                     ),
)


class IProposal(proposal.IProposal):
    """BPlan proposal versions pool."""


proposal_meta = proposal.proposal_meta._replace(
    iresource=IProposal,
    element_types=(IProposalVersion,),
    item_type=IProposalVersion,
    default_workflow='bplan_private',
)


class IProcess(process.IProcess):
    """BPlan participation process."""


process_meta = process.process_meta._replace(
    content_name='BplanProcess',
    iresource=IProcess,
    element_types=(IProposal,
                   ),
    is_implicit_addable=True,
    default_workflow='bplan',
    extended_sheets=(adhocracy_meinberlin.sheets.bplan.IProcessSettings,
                     adhocracy_meinberlin.sheets.bplan.IProcessPrivateSettings,
                     adhocracy_core.sheets.image.IImageReference,
                     ),
)


def embed_code_config_bplan_adapter(context: IResource,
                                    request: IRequest) -> {}:
    """Return config to render `adhocracy_core:templates/embed_code.html`."""
    mapping = embed_code_config_adapter(context, request)
    mapping.update({'widget': 'mein-berlin-bplaene-proposal-embed',
                    'style': 'height: 650px',
                    'noheader': 'true',
                    })
    return mapping


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(proposal_version_meta, config)
    add_resource_type_to_registry(process_meta, config)
    config.registry.registerAdapter(embed_code_config_bplan_adapter,
                                    (IProcess, IRequest),
                                    IEmbedCodeConfig)
