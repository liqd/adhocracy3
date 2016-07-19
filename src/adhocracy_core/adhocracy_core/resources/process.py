"""Basic participation process."""
from pyramid.i18n import TranslationStringFactory
from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import pool_meta
from adhocracy_core.resources.asset import add_assets_service
from adhocracy_core.resources.badge import add_badges_service
from adhocracy_core.sheets.asset import IHasAssetPool
from adhocracy_core.sheets.badge import IHasBadgesPool
from adhocracy_core.sheets.description import IDescription
from adhocracy_core.sheets.notification import IFollowable


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
                     IFollowable,
                     ))


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(process_meta, config)
