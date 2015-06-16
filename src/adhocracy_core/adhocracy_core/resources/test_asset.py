from unittest.mock import Mock

from pytest import fixture
from pytest import mark
from pytest import raises
import colander

from adhocracy_core.sheets.image import IImageMetadata
from adhocracy_core.resources.image import IImage


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
    assert meta.element_types == [IAsset]


def test_pool_with_assets_meta():
    from .asset import add_assets_service
    from .asset import IPoolWithAssets
    from .asset import pool_with_assets_meta
    from adhocracy_core.sheets.asset import IHasAssetPool
    meta = pool_with_assets_meta
    assert meta.iresource is IPoolWithAssets
    assert IHasAssetPool in meta.basic_sheets
    assert add_assets_service in meta.after_creation


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources')


@mark.usefixtures('integration')
class TestAsset:

    @fixture
    def context(self, pool):
        return pool

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
                    resource_type=IImage,
                    asset_metadata_sheet=IImageMetadata):
        from adhocracy_core.sheets.asset import IAssetData
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

    def test_valid(self, pool, registry):
        from adhocracy_core.resources.asset import validate_and_complete_asset
        asset = self._make_asset(pool, registry)
        validate_and_complete_asset(asset, registry)
        assert 'raw' in asset
        assert 'thumbnail' in asset

    def test_valid_call_twice(self, pool, registry):
        """Calling it twice should delete and re-create the child nodes."""
        from adhocracy_core.resources.asset import validate_and_complete_asset
        asset = self._make_asset(pool, registry)
        validate_and_complete_asset(asset, registry)
        old_raw = asset['raw']
        validate_and_complete_asset(asset, registry)
        assert asset['raw'] != old_raw

    def test_mime_type_mismatch(self, pool, registry):
        from adhocracy_core.resources.asset import validate_and_complete_asset
        asset = self._make_asset(pool, registry, mime_type='image/jpg')
        with raises(colander.Invalid) as err_info:
            validate_and_complete_asset(asset, registry)
        assert 'Claimed MIME type' in err_info.value.msg

    def test_invalid_mime_type(self, pool, registry):
        from adhocracy_core.resources.asset import validate_and_complete_asset
        asset = self._make_asset(pool, registry,
                                 mime_type='text/plain',
                                 mime_type_in_file='text/plain')
        with raises(colander.Invalid) as err_info:
            validate_and_complete_asset(asset, registry)
        assert 'Invalid MIME type' in err_info.value.msg

    def test_abstract_sheet(self, pool, registry):
        from adhocracy_core.resources.asset import IAsset
        from adhocracy_core.resources.asset import validate_and_complete_asset
        from adhocracy_core.sheets.asset import IAssetMetadata
        asset = self._make_asset(pool, registry,
                                 resource_type=IAsset,
                                 asset_metadata_sheet=IAssetMetadata)
        with raises(colander.Invalid) as err_info:
            validate_and_complete_asset(asset, registry)
        assert 'Sheet is abstract' in err_info.value.msg
