from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import raises


def test_includeme_register_has_asset_pool_sheet(config):
    from adhocracy_core.sheets.asset import IHasAssetPool
    from adhocracy_core.utils import get_sheet
    config.include('adhocracy_core.sheets.asset')
    context = testing.DummyResource(__provides__=IHasAssetPool)
    assert get_sheet(context, IHasAssetPool)


class TestIHasAssetPoolSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.asset import has_asset_pool_meta
        return has_asset_pool_meta

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.asset import IHasAssetPool
        from adhocracy_core.sheets.asset import HasAssetPoolSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IHasAssetPool
        assert inst.meta.schema_class == HasAssetPoolSchema

    def test_get_without_asset_service(self, meta, context, mock_graph):
        from adhocracy_core.exceptions import RuntimeConfigurationError
        inst = meta.sheet_class(meta, context)
        mock_graph.get_references_for_isheet.return_value = {}
        mock_graph.get_back_references_for_isheet.return_value = {}
        with raises(RuntimeConfigurationError):
            inst.get()

    @fixture
    def mock_asset_pool(self, monkeypatch):
        from adhocracy_core import schema
        asset_pool = testing.DummyResource()
        mock_get_post_pool = Mock(spec=schema._get_post_pool,
                                  return_value=asset_pool)
        monkeypatch.setattr(schema, '_get_post_pool', mock_get_post_pool)
        return asset_pool

    def test_get_with_asset_service(self, meta, context, mock_graph,
                                          mock_asset_pool):
        inst = meta.sheet_class(meta, context)
        mock_graph.get_references_for_isheet.return_value = {}
        mock_graph.get_back_references_for_isheet.return_value = {}
        data = inst.get()
        assert data['asset_pool'] == mock_asset_pool
