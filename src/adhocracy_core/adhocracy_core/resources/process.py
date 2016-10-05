"""Basic participation process."""
from pyramid.i18n import TranslationStringFactory
from pyramid.interfaces import IRequest
from pyramid.traversal import resource_path
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IResource
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import pool_meta
from adhocracy_core.resources.asset import add_assets_service
from adhocracy_core.resources.badge import add_badges_service
from adhocracy_core.sheets.asset import IHasAssetPool
from adhocracy_core.sheets.badge import IHasBadgesPool
from adhocracy_core.sheets.description import IDescription
from adhocracy_core.sheets.embed import IEmbed
from adhocracy_core.sheets.embed import IEmbedCodeConfig
from adhocracy_core.sheets.embed import embed_code_config_adapter
from adhocracy_core.sheets.notification import IFollowable
from adhocracy_core.sheets.anonymize import IAllowAddAnonymized


_ = TranslationStringFactory('adhocracy')


class IProcess(IPool):
    """Participation Process Pool."""


process_meta = pool_meta._replace(
    content_name=_('Process'),
    iresource=IProcess,
    permission_create='create_process',
    is_sdi_addable=True,
    after_creation=(add_assets_service,
                    add_badges_service,
                    ),
    default_workflow='sample',
    alternative_workflows=(
        'standard',
        'standard_private',
        'debate',
        'debate_private',
    )
)._add(basic_sheets=(IHasAssetPool,
                     IHasBadgesPool,
                     IDescription,
                     IEmbed,
                     IFollowable,
                     IAllowAddAnonymized,
                     ))


def process_embed_code_config_adapter(context: IResource,
                                      request: IRequest) -> {}:
    """Return config to render `adhocracy_core:templates/embed_code.html`."""
    mapping = embed_code_config_adapter(context, request)
    initial_url = '/r' + resource_path(context) + '/'
    mapping.update({'widget': 'plain',
                    'autourl': 'true',
                    'initial_url': initial_url,
                    'style': 'height: 650px',
                    })
    return mapping


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(process_meta, config)
    config.registry.registerAdapter(process_embed_code_config_adapter,
                                    (IProcess, IRequest),
                                    IEmbedCodeConfig)
