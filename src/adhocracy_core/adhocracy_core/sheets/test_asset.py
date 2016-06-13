from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark


class TestIHasAssetPoolSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.asset import has_asset_pool_meta
        return has_asset_pool_meta

    @fixture
    def context(self, pool, service, mock_graph):
        pool['assets'] = service
        pool.__graph__ = mock_graph
        return pool

    def test_create_valid(self, meta, context):
        from . import asset
        inst = meta.sheet_class(meta, context, None)
        assert inst.meta.isheet == asset.IHasAssetPool
        assert inst.meta.schema_class == asset.HasAssetPoolSchema

    def test_get_with_asset_service(self, meta, context, service):
        inst = meta.sheet_class(meta, context, None)
        data = inst.get()
        assert data['asset_pool'] == service

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, service, pool, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        pool['assets'] = service
        pool['context'] = context
        assert registry.content.get_sheet(context, meta.isheet)


class TestIAssetMetadata:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.asset import asset_metadata_meta
        return asset_metadata_meta

    def test_create_valid(self, meta, context):
        from . import asset
        inst = meta.sheet_class(meta, context, None)
        assert inst.meta.isheet == asset.IAssetMetadata
        assert inst.meta.schema_class == asset.AssetMetadataSchema

    def test_get(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'attached_to': [],
                              'filename': '',
                              'mime_type': '',
                              'size': 0,
                              }

    def test_get_with_backreference(self, meta, context, sheet_catalogs,
                                    search_result, registry):
        inst = meta.sheet_class(meta, context, registry)
        attacher = testing.DummyResource()
        sheet_catalogs.search.return_value =\
            search_result._replace(elements=[attacher])
        assert inst.get()['attached_to'] == [attacher]

    def test_set_and_get(self, meta, context, registry):
        inst = meta.sheet_class(meta, context, registry)
        inst.set({'filename': 'dummy.jpg',
                  'mime_type': 'image/jpeg',
                  'size': 890828},
                  omit_readonly=False)
        appstruct = inst.get()
        assert appstruct['filename'] == 'dummy.jpg'
        assert appstruct['mime_type'] == 'image/jpeg'
        assert appstruct['size'] == 890828

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)


class TestIAssetData:

    @fixture
    def meta(self):
        from .asset import asset_data_meta
        return asset_data_meta

    def test_meta(self, meta):
        from . import asset
        assert meta.isheet == asset.IAssetData
        assert meta.schema_class == asset.AssetDataSchema
        assert meta.readable is False

    def test_create(self, meta, context):
        from .asset import deferred_validate_asset_mime_type
        inst = meta.sheet_class(meta, context, None)
        inst.schema['data'].widget == deferred_validate_asset_mime_type

    def test_get(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'data': None}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)


class TestDeferredValidateAssetMimeType:

    def call_fut(self, *args):
        from .asset import deferred_validate_asset_mime_type
        return deferred_validate_asset_mime_type(*args)

    def test_ignore_if_no_image(self, node, context):
        kw = {'context': context,
              'creating': None }
        assert self.call_fut(node, kw) is None

    def test_validate_mimetype_if_editing_image(self, node):
        from adhocracy_core.resources.image import IImage
        from .image import validate_image_data_mimetype
        context = testing.DummyResource(__provides__=IImage)
        kw = {'context': context,
              'creating': None}
        assert self.call_fut(node, kw) == validate_image_data_mimetype

    def test_validate_mimetype_if_creating_image(self, node, context,
                                                 resource_meta):
        from adhocracy_core.sheets.image import validate_image_data_mimetype
        from adhocracy_core.resources.image import IImage
        creating = resource_meta._replace(iresource=IImage)
        kw = {'context': context,
              'creating': creating}
        assert self.call_fut(node, kw) == validate_image_data_mimetype
