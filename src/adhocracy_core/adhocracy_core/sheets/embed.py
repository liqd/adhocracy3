"""Embed Sheet."""
import os.path

from colander import deferred
from pyramid.interfaces import IRequest
from pyramid.renderers import render
from zope.interface import Interface

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IResource
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Text
from adhocracy_core.schema import URL


class IEmbed(ISheet):
    """Market interface for the embed sheet."""


class IEmbedCodeConfig(Interface):
    """Interface for embed code config mappings."""


def embed_code_config_adapter(context: IResource,
                              request: IRequest) -> {}:
    """Return mapping to render `adhocracy_core:templates/embed_code.html`."""
    settings = request.registry.settings
    frontend_url = settings.get('adhocracy.frontend_url',
                                'http://localhost:6551')
    sdk_url = os.path.join(frontend_url, 'AdhocracySDK.js')
    path = request.resource_url(context)
    locale = settings.get('pyramid.default_locale_name', 'en')
    return {'sdk_url': sdk_url,
            'frontend_url': frontend_url,
            'path': path,
            'widget': '',
            'autoresize': 'false',
            'locale': locale,
            'autourl': 'false',
            'initial_url': '',
            'nocenter': 'true',
            'noheader': 'false',
            'style': 'height: 650px',
            }


@deferred
def deferred_default_embed_code(node: MappingSchema, kw: dict) -> str:
    """Return html code to embed the current `context` resource."""
    context = kw['context']
    request = kw.get('request', None)
    if request is None:
        return ''
    mapping = request.registry.getMultiAdapter((context, request),
                                               IEmbedCodeConfig)
    code = render('adhocracy_core:templates/embed_code.html.mako', mapping)
    return code


class EmbedSchema(MappingSchema):
    """Embed sheet data structure.

    `embed_code`: html code to embed the `context` resource in web pages.
    `external_url`: canonical URL that embeds the `context` resource.
    """

    embed_code = Text(readonly=True,
                      default=deferred_default_embed_code,
                      )
    external_url = URL()


embed_meta = sheet_meta._replace(isheet=IEmbed,
                                 schema_class=EmbedSchema,
                                 )


def includeme(config):
    """Register sheets and embed code config adapter."""
    add_sheet_to_registry(embed_meta, config.registry)
    config.registry.registerAdapter(embed_code_config_adapter,
                                    (IResource, IRequest),
                                    IEmbedCodeConfig)
