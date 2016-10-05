"""Embed Sheet."""
from pyramid.interfaces import IRequest

from adhocracy_core.interfaces import IResource
from adhocracy_core.sheets.embed import embed_code_config_adapter
from adhocracy_core.sheets.embed import IEmbedCodeConfig
from adhocracy_meinberlin.resources.bplan import IProcess


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
    """Register embed code config adapter."""
    config.registry.registerAdapter(embed_code_config_bplan_adapter,
                                    (IProcess, IRequest),
                                    IEmbedCodeConfig)
