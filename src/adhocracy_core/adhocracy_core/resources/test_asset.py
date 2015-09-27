from unittest.mock import Mock

from pytest import fixture
from pytest import mark
from pytest import raises
import colander


def test_asset_meta():
    from .asset import asset_meta
    from adhocracy_core.resources.asset import IAsset
    from adhocracy_core.sheets.metadata import IMetadata
    from adhocracy_core.sheets.asset import IAssetData
    from adhocracy_core.sheets.asset import IAssetMetadata
    from adhocracy_core.sheets.title import ITitle
    meta = asset_meta
    assert meta.iresource is IAsset
    assert IMetadata in meta.basic_sheets
    assert IAssetData in meta.basic_sheets
    assert ITitle in meta.basic_sheets
    assert IAssetMetadata in meta.extended_sheets
    assert meta.use_autonaming
    assert meta.permission_create == 'create_asset'


def test_assets_service_meta():
    from .asset import assets_service_meta
    from .asset import IAssetsService
    from adhocracy_core.resources.asset import IAsset
    meta = assets_service_meta
    assert meta.iresource is IAssetsService
    assert meta.element_types == (IAsset,)


def test_pool_with_assets_meta():
    from .asset import add_assets_service
    from .asset import IPoolWithAssets
    from .asset import pool_with_assets_meta
    from adhocracy_core.sheets.asset import IHasAssetPool
    meta = pool_with_assets_meta
    assert meta.iresource is IPoolWithAssets
    assert IHasAssetPool in meta.basic_sheets
    assert add_assets_service in meta.after_creation


@mark.usefixtures('integration')
class TestAsset:

    @fixture
    def context(self, pool):
        return pool

    @fixture
    def meta(self):
        from .asset import asset_meta
        return asset_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import ISimple
        import adhocracy_core.sheets
        from .asset import IAsset
        from .asset import validate_and_complete_asset
        assert meta.iresource is IAsset
        assert meta.iresource.isOrExtends(ISimple)
        assert meta.permission_create == 'create_asset'
        assert meta.basic_sheets == (adhocracy_core.sheets.metadata.IMetadata,
                                     adhocracy_core.sheets.asset.IAssetData,
                                     adhocracy_core.sheets.title.ITitle,
                                     )
        assert meta.extended_sheets == (
            adhocracy_core.sheets.asset.IAssetMetadata,)
        assert meta.use_autonaming
        assert validate_and_complete_asset in meta.after_creation

    def test_create_asset(self, context, registry):
        from adhocracy_core.resources.asset import IAsset
        res = registry.content.create(IAsset.__identifier__, context)
        assert IAsset.providedBy(res)

    def test_add_assets_service(self, context, registry):
        from .asset import add_assets_service
        from .asset import IAssetsService
        add_assets_service(context, registry, {})
        assert context['assets']
        assert IAssetsService.providedBy(context['assets'])

    def test_create_pool_with_assets(self, registry):
        from .asset import IPoolWithAssets
        res = registry.content.create(IPoolWithAssets.__identifier__)
        assert IPoolWithAssets.providedBy(res)

    def test_create_assets_service(self, context, registry):
        from .asset import IAssetsService
        from substanced.util import find_service
        res = registry.content.create(IAssetsService.__identifier__, context)
        assert IAssetsService.providedBy(res)
        assert find_service(context, 'assets')


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
        from .asset import validate_and_complete_asset
        return validate_and_complete_asset(*args)

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

    def test_mime_type_mismatch(self, pool, registry):
        asset = self._make_asset(pool, registry,
                                 mime_type='text/plain',
                                 mime_type_in_file='wrong')
        with raises(colander.Invalid) as err_info:
            self.call_fut(asset, registry)
        assert 'Claimed MIME type' in err_info.value.msg

    def test_invalid_mime_type(self, pool, registry):
        from adhocracy_core.sheets.asset import IAssetMetadata
        asset = self._make_asset(pool, registry)
        sheets_meta = registry.content.sheets_meta
        sheets_meta[IAssetMetadata] = sheets_meta[IAssetMetadata]._replace(
            mime_type_validator=lambda x: False)
        with raises(colander.Invalid) as err_info:
            self.call_fut(asset, registry)
        assert 'Invalid MIME type' in err_info.value.msg

    def test_abstract_sheet(self, pool, registry):
        from adhocracy_core.resources.asset import IAsset
        from adhocracy_core.sheets.asset import IAssetMetadata
        asset = self._make_asset(pool, registry)
        metas = registry.content.sheets_meta
        metas[IAssetMetadata] = metas[IAssetMetadata]._replace(
            mime_type_validator=None)
        with raises(colander.Invalid) as err_info:
            self.call_fut(asset, registry)
        assert 'Sheet is abstract' in err_info.value.msg
