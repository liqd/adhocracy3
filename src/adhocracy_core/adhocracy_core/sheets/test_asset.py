from pyramid import testing
from pytest import fixture


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

    @fixture
    def context(self, pool, service, mock_graph):
        pool.__graph__ = mock_graph
        return pool

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

    def test_get_empty(self, meta, context, mock_graph):
        inst = meta.sheet_class(meta, context)
        mock_graph.get_references_for_isheet.return_value = {}
        mock_graph.get_back_references_for_isheet.return_value = {}
        data = inst.get()
        assert data['asset_pool'] == ''

    def test_get_with_asset_pool(self, meta, context, mock_graph):
        asset_pool = testing.DummyResource()
        inst = meta.sheet_class(meta, context)
        mock_graph.get_references_for_isheet.return_value = {'asset_pool':
                                                             [asset_pool]}
        mock_graph.get_back_references_for_isheet.return_value = {}
        data = inst.get()
        assert data['asset_pool'] == asset_pool

    def test_set_with_asset_pool(self, meta, context, mock_graph):
        asset_pool = testing.DummyResource()
        mock_graph.get_references_for_isheet.return_value = {}
        inst = meta.sheet_class(meta, context)
        inst.set({'asset_pool': asset_pool})
        assert 'asset_pool' not in inst._data
