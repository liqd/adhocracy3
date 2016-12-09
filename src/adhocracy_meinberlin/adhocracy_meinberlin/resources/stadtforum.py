"""Stadtforum process resources."""
from pyramid.interfaces import IRequest

from adhocracy_core.interfaces import IResource
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal
from adhocracy_core.sheets.embed import IEmbed
from adhocracy_core.sheets.embed import IEmbedCodeConfig
from adhocracy_core.sheets.embed import embed_code_config_adapter
from adhocracy_core.sheets.image import IImageReference


class IPoll(proposal.IProposal):
    """Poll."""


poll_meta = proposal.proposal_meta._replace(
    iresource=IPoll,
    default_workflow='stadtforum_poll',
    autonaming_prefix='poll_',
)._add(extended_sheets=(IEmbed,
                        ))


class IProcess(process.IProcess):
    """Stadtforum participation process."""


process_meta = process.process_meta._replace(
    content_name='StadtForumProcess',
    iresource=IProcess,
    element_types=(IPoll,
                   ),
    is_implicit_addable=True,
    default_workflow='stadtforum',
    extended_sheets=(
        IImageReference,
    ),
)


def embed_code_config_poll_adapter(context: IResource,
                                   request: IRequest) -> {}:
    """Return config to render `adhocracy_core:templates/embed_code.html`."""
    mapping = embed_code_config_adapter(context, request)
    version_path = mapping['path'] + 'VERSION_0000000/'
    mapping.update({'widget': 'meinberlin-stadtforum-proposal-detail',
                    'autoresize': 'false',
                    'autourl': 'false',
                    'nocenter': 'true',
                    'noheader': 'true',
                    'path': version_path
                    })
    return mapping


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(process_meta, config)
    add_resource_type_to_registry(poll_meta, config)
    config.registry.registerAdapter(embed_code_config_poll_adapter,
                                    (IPoll, IRequest),
                                    IEmbedCodeConfig)
