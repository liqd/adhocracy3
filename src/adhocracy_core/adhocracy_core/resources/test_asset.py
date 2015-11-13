from unittest.mock import Mock

from pytest import fixture
from pytest import mark
from pytest import raises
from pyramid import testing


class TestAssetDownload:

    @fixture
    def registry(self, registry_with_content, mock_sheet):
        registry = registry_with_content
        registry.content.get_sheet.return_value = mock_sheet
        return registry

    @fixture
    def meta(self):
        from .asset import asset_download_meta
        return asset_download_meta

    @fixture
    def asset(self):
      from adhocracy_core.sheets.asset import IAssetData
      return testing.DummyResource(__provides__=IAssetData)

    @fixture
    def inst(self, meta):
        inst = meta.content_class()
        return inst

    def test_meta(self, meta):
        from adhocracy_core.interfaces import IResource
        from . import asset
        assert meta.iresource is asset.IAssetDownload
        assert meta.iresource.isOrExtends(IResource)
        assert meta.content_class == asset.AssetDownload
        assert meta.permission_create == 'create_asset_download'
        assert meta.use_autonaming

    def test_get_response_return_asset_parent_data(self, inst, registry,
                                                   mock_sheet, asset):
        asset['download'] = inst
        file = Mock()
        mock_sheet.get.return_value = {'data': file}
        assert inst.get_response(registry) == file.get_response.return_value

    def test_get_response_raise_if_no_asset_parent(self, inst, registry):
        from adhocracy_core.exceptions import RuntimeConfigurationError
        with raises(RuntimeConfigurationError):
            assert inst.get_response(registry)

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


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
        assert meta.after_creation == (asset.add_metadata,)

    @mark.usefixtures('integration')
    def test_create(self, registry, meta, pool):
        from adhocracy_core.sheets.asset import IAssetData
        from adhocracy_core.sheets.asset import IAssetMetadata
        from .asset import IAssetDownload
        from adhocracy_core.utils import get_sheet
        file = Mock(mimetype='image/png', size=100, title='title')
        appstructs = {IAssetData.__identifier__: {'data': file}}
        res = registry.content.create(meta.iresource.__identifier__,
                                      appstructs=appstructs,
                                      parent=pool)
        meta = get_sheet(res, IAssetMetadata).get()
        assert meta['filename'] == 'title'
        assert meta['size'] == 100


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

