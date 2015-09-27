from unittest.mock import Mock

from pytest import fixture
from pytest import mark
from pytest import raises
import colander


class TestAsset:

    @fixture
    def meta(self):
        from .asset import asset_meta
        return asset_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import ISimple
        from . import asset
        import adhocracy_core.sheets
        assert meta.iresource is asset.IAsset
        assert meta.iresource.isOrExtends(ISimple)
        assert meta.permission_create == 'create_asset'
        assert meta.basic_sheets == (adhocracy_core.sheets.metadata.IMetadata,
                                     adhocracy_core.sheets.asset.IAssetData,
                                     adhocracy_core.sheets.title.ITitle,
                                     )
        assert meta.extended_sheets == (
            adhocracy_core.sheets.asset.IAssetMetadata,)
        assert meta.use_autonaming
        assert asset.store_asset_meta_and_add_downloads in meta.after_creation

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestAssetsService:

    @fixture
    def meta(self):
        from .asset import assets_service_meta
        return assets_service_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import IServicePool
        from . import asset
        assert meta.iresource is asset.IAssetsService
        assert meta.iresource.isOrExtends(IServicePool)
        assert meta.element_types == (asset.IAsset,)

    @mark.usefixtures('integration')
    def test_create(self, pool, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__, pool)

    @mark.usefixtures('integration')
    def test_add_assets_service(self, pool, registry, meta):
        from substanced.util import find_service
        from .asset import add_assets_service
        add_assets_service(pool, registry, {})
        assert find_service(pool, 'assets')


@mark.usefixtures('integration')
class TestValidateAndCompleteAsset:

    def _make_asset(self, pool, registry,
                    mime_type='image/png',
                    mime_type_in_file='image/png',
                    resource_type=None,
                    asset_metadata_sheet=None):
        from .asset import IAsset
        from adhocracy_core.sheets.asset import IAssetData
        from adhocracy_core.sheets.asset import IAssetMetadata
        resource_type = resource_type or IAsset
        asset_metadata_sheet = asset_metadata_sheet or IAssetMetadata
        mock_file = Mock()
        mock_file.mimetype = mime_type_in_file
        appstructs = {IAssetData.__identifier__: {
                          'data': mock_file},
                      asset_metadata_sheet.__identifier__: {
                          'mime_type': mime_type}}
        return registry.content.create(resource_type.__identifier__,
                                       appstructs=appstructs,
                                       parent=pool,
                                       run_after_creation=False)

    def call_fut(self, *args):
        from .asset import store_asset_meta_and_add_downloads
        return store_asset_meta_and_add_downloads(*args)

    def test_add_download_raw(self, pool, registry):
        from adhocracy_core.sheets.asset import IAssetMetadata
        from .asset import IAssetDownload
        asset = self._make_asset(pool, registry, )
        self.call_fut(asset, registry)
        metadata = registry.content.get_sheet(asset, IAssetMetadata)
        raw = metadata.get()['raw']
        assert IAssetDownload.providedBy(raw)

    def test_add_downloads_for_image_resize(self, pool, registry):
        # TODO refactor && move this test to .test_image
        from .image import IImage
        from adhocracy_core.sheets.image import IImageMetadata
        from .asset import IAssetDownload
        asset = self._make_asset(pool, registry,
                                 resource_type=IImage,
                                 asset_metadata_sheet=IImageMetadata)
        self.call_fut(asset, registry)
        metadata = registry.content.get_sheet(asset, IImageMetadata)
        detail = metadata.get()['detail']
        assert IAssetDownload.providedBy(detail)



