"""Resources for managing assets."""

from pyramid.registry import Registry

from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.interfaces import ISimple
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import IBasicPool
from adhocracy_core.resources.pool import basicpool_metadata
from adhocracy_core.resources.service import service_metadata
from adhocracy_core.resources.simple import simple_metadata
import adhocracy_core.sheets.asset


class IPoolWithAssets(IBasicPool):

    """A pool with an auto-created asset pool."""


class IAsset(ISimple):

    """A generic asset."""


asset_meta = simple_metadata._replace(
    content_name='Asset',
    iresource=IAsset,
    basic_sheets=simple_metadata.basic_sheets + [
        adhocracy_core.sheets.asset.IAssetMetadata,
        adhocracy_core.sheets.asset.IAssetData
    ],
    use_autonaming=True,
    permission_add='add_asset',
)


class IAssetsService(IServicePool):

    """The 'assets' ServicePool."""


assets_service_meta = service_metadata._replace(
    iresource=IAssetsService,
    content_name='assets',
    element_types=[IAsset],
)


def add_assets_service(context: IPool, registry: Registry, options: dict):
    """Add `assets` service to context."""
    registry.content.create(IAssetsService.__identifier__, parent=context)


pool_with_assets_meta = basicpool_metadata._replace(
    iresource=IPoolWithAssets,
    basic_sheets=basicpool_metadata.basic_sheets + [
        adhocracy_core.sheets.asset.IHasAssetPool],
    after_creation=basicpool_metadata.after_creation + [add_assets_service],
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(asset_meta, config)
    add_resource_type_to_registry(assets_service_meta, config)
    add_resource_type_to_registry(pool_with_assets_meta, config)
