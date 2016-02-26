"""Resources for managing assets."""

from substanced.file import File
from pyramid.registry import Registry
from pyramid.response import FileResponse
from pyramid.traversal import find_interface
from zope.deprecation import deprecated

from adhocracy_core.exceptions import RuntimeConfigurationError
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.interfaces import ISimple
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.base import Base
from adhocracy_core.resources.pool import pool_meta
from adhocracy_core.resources.service import service_meta
from adhocracy_core.resources import resource_meta
from adhocracy_core.sheets.asset import IAssetData
from adhocracy_core.sheets.asset import IAssetMetadata
from adhocracy_core.utils import get_matching_isheet
from adhocracy_core.utils import get_sheet_field
import adhocracy_core.sheets.metadata
import adhocracy_core.sheets.asset
import adhocracy_core.sheets.title


class IAssetDownload(IResource):
    """Downloadable binary file for Assets."""


class AssetDownload(Base):
    """Allow downloading the first asset file in the term:`lineage`."""

    def get_response(self, registry: Registry=None) -> FileResponse:
        """Return response with binary content of the asset data."""
        file = self._get_asset_file_in_lineage(registry)
        return file.get_response()

    def _get_asset_file_in_lineage(self, registry) -> File:
        asset = find_interface(self, IAssetData)
        if asset is None:
            msg = 'No IAssetData in lineage of {}'.format(self)
            raise RuntimeConfigurationError(details=msg)
        return get_sheet_field(asset, IAssetData, 'data', registry)


asset_download_meta = resource_meta._replace(
    content_name='AssetDownload',
    iresource=IAssetDownload,
    use_autonaming=True,
    content_class=AssetDownload,
    permission_create='create_asset_download'
)


class IAsset(ISimple):
    """A generic asset (binary file)."""


def add_metadata(context: IAsset, registry: Registry, **kwargs):
    """Store asset file metadata and add `raw` download to `context`."""
    file = get_sheet_field(context, IAssetData, 'data', registry=registry)
    meta_isheet = get_matching_isheet(context, IAssetMetadata)
    meta_sheet = registry.content.get_sheet(context, meta_isheet)
    meta_appstruct = {
        'size': file.size,
        'filename': file.title,
    }
    meta_sheet.set(meta_appstruct, omit_readonly=False)


asset_meta = pool_meta._replace(
    content_name='Asset',
    iresource=IAsset,
    basic_sheets=(
        adhocracy_core.sheets.metadata.IMetadata,
        adhocracy_core.sheets.asset.IAssetData,
        adhocracy_core.sheets.title.ITitle,
    ),
    extended_sheets=(
        # all subtypes need to provide an IAssetMetadata sheet
        adhocracy_core.sheets.asset.IAssetMetadata,
    ),
    use_autonaming=True,
    permission_create='create_asset',
    after_creation=(add_metadata,),
)


class IAssetsService(IServicePool):
    """The 'assets' ServicePool."""


assets_service_meta = service_meta._replace(
    iresource=IAssetsService,
    content_name='assets',
    element_types=(IAsset,),
)


class IPoolWithAssets(IPool):
    """A pool with an auto-created asset service pool."""


deprecated('IPoolWithAssets', 'Backward compatible code, use process instead')


def add_assets_service(context: IPool, registry: Registry, options: dict):
    """Add `assets` service to context."""
    registry.content.create(IAssetsService.__identifier__, parent=context,
                            registry=registry)


pool_with_assets_meta = pool_meta._replace(
    iresource=IPoolWithAssets,
    after_creation=(add_assets_service,),
    is_implicit_addable=True,
)._add(basic_sheets=(adhocracy_core.sheets.asset.IHasAssetPool,))


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(asset_download_meta, config)
    add_resource_type_to_registry(asset_meta, config)
    add_resource_type_to_registry(assets_service_meta, config)
    add_resource_type_to_registry(pool_with_assets_meta, config)
