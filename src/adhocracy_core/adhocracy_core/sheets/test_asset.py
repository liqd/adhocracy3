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
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == asset.IHasAssetPool
        assert inst.meta.schema_class == asset.HasAssetPoolSchema

    def test_get_with_asset_service(self, meta, context, mock_graph, service):
        inst = meta.sheet_class(meta, context)
        data = inst.get()
        assert data['asset_pool'] == service

    @mark.usefixtures('integration')
    def test_includeme_register_has_asset_pool_sheet(registry, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestIAssetMetadata:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.asset import asset_metadata_meta
        return asset_metadata_meta

    def test_create_valid(self, meta, context):
        from . import asset
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == asset.IAssetMetadata
        assert inst.meta.schema_class == asset.AssetMetadataSchema

    def test_get(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'attached_to': [],
                              'filename': '',
                              'mime_type': '',
                              'size': 0,
                              'raw': None}

    def test_get_with_backreference(self, meta, context, sheet_catalogs,
                                    search_result):
        inst = meta.sheet_class(meta, context)
        attacher = testing.DummyResource()
        sheet_catalogs.search.return_value =\
            search_result._replace(elements=[attacher])
        assert inst.get()['attached_to'] == [attacher]

    def test_set_and_get(self, meta, context):
        inst = meta.sheet_class(meta, context)
        inst.set({'filename': 'dummy.jpg',
                  'mime_type': 'image/jpeg',
                  'size': 890828},
                  omit_readonly=False)
        appstruct = inst.get()
        assert appstruct['filename'] == 'dummy.jpg'
        assert appstruct['mime_type'] == 'image/jpeg'
        assert appstruct['size'] == 890828

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestAssetFileDownload:

    @fixture
    def inst(self):
        from adhocracy_core.sheets.asset import AssetFileDownload
        return AssetFileDownload()

    @fixture
    def inst_with_dimensions(self):
        from adhocracy_core.sheets.asset import AssetFileDownload
        from adhocracy_core.interfaces import Dimensions
        return AssetFileDownload(Dimensions(width=200, height=100))

    def test_get_response_without_dimensions_and_file(self, inst, context,
                                                      registry, monkeypatch):
        from adhocracy_core.sheets import asset
        from substanced.file import File
        parent = testing.DummyResource()
        context.__parent__ = parent
        file = Mock(spec=File)
        dummy_response = testing.DummyResource()
        file.get_response.return_value = dummy_response
        mock_retrieve_asset_file = Mock(spec=asset.retrieve_asset_file,
                                        return_value=file)
        monkeypatch.setattr(asset, 'retrieve_asset_file',
                            mock_retrieve_asset_file)
        assert inst.get_response(context, registry) == dummy_response
        assert mock_retrieve_asset_file.called
        assert mock_retrieve_asset_file.call_args[0] == (parent, registry)

    def test_get_response_with_dimensions_and_without_file(
            self, inst_with_dimensions, context, registry, monkeypatch):
        from adhocracy_core.sheets.asset import AssetFileDownload
        from substanced.file import File
        file = Mock(spec=File)
        dummy_response = testing.DummyResource()
        file.get_response.return_value = dummy_response
        mock_crop_and_resize_image = Mock(
            spec=AssetFileDownload._crop_and_resize_image, return_value=file)
        monkeypatch.setattr(inst_with_dimensions, '_crop_and_resize_image',
                            mock_crop_and_resize_image)
        assert inst_with_dimensions.get_response(context,
                                                 registry) == dummy_response
        assert mock_crop_and_resize_image.called
        assert mock_crop_and_resize_image.call_args[0] == (context, registry)

    def test_get_response_with_file(self, inst, context, registry):
        from substanced.file import File
        file = Mock(spec=File)
        dummy_response = testing.DummyResource()
        file.get_response.return_value = dummy_response
        inst.file = file
        assert inst.get_response(context, registry) == dummy_response

    def test_crop_and_resize_image(self, inst_with_dimensions, context,
                                   registry, monkeypatch):
        import io
        from PIL import Image
        from substanced.file import File
        from adhocracy_core.sheets import asset
        from adhocracy_core.interfaces import Dimensions
        file = Mock(spec=File)
        file.blob = Mock()
        file.blob.open.return_value = io.BytesIO(b'dummy blob')
        file.mimetype = 'image/png'
        mock_retrieve_asset_file = Mock(spec=asset.retrieve_asset_file,
                                        return_value=file)
        monkeypatch.setattr(asset, 'retrieve_asset_file',
                            mock_retrieve_asset_file)
        mock_image = Mock()
        mock_image.size = (840, 700)
        mock_crop_image = Mock()
        mock_image.crop.return_value = mock_crop_image
        mock_open = Mock(spec=Image.open, return_value=mock_image)
        monkeypatch.setattr(Image, 'open', mock_open)
        dimensions = Dimensions(width=200, height=100)
        result = inst_with_dimensions._crop_and_resize_image(context, registry)
        assert file.blob.open.called
        assert mock_image.crop.called
        assert mock_crop_image.resize.called
        assert mock_crop_image.resize.call_args[0] == (dimensions,
                                                       Image.ANTIALIAS)
        assert result == inst_with_dimensions.file
        assert result.mimetype == file.mimetype

    def test_crop_if_needed_crop_height(self, inst_with_dimensions):
        mock_image = Mock()
        mock_image.size = (840, 700)
        crop_result = Mock()
        mock_image.crop.return_value = crop_result
        assert inst_with_dimensions._crop_if_needed(mock_image) == crop_result
        assert mock_image.crop.called
        assert mock_image.crop.call_args[0][0] == (0, 140, 840, 560)

    def test_crop_if_needed_crop_width(self, inst_with_dimensions):
        mock_image = Mock()
        mock_image.size = (1000, 400)
        crop_result = Mock()
        mock_image.crop.return_value = crop_result
        assert inst_with_dimensions._crop_if_needed(mock_image) == crop_result
        assert mock_image.crop.called
        assert mock_image.crop.call_args[0][0] == (100, 0, 900, 400)

    def test_crop_if_needed_no_cropping_needed(self, inst_with_dimensions):
        mock_image = Mock()
        mock_image.size = (800, 400)
        assert inst_with_dimensions._crop_if_needed(mock_image) == mock_image
        assert not mock_image.crop.called

    def test_crop_if_needed_no_cropping_needed_due_to_rounding(
            self, inst_with_dimensions):
        mock_image = Mock()
        mock_image.size = (999, 500)
        assert inst_with_dimensions._crop_if_needed(mock_image) == mock_image
        assert not mock_image.crop.called


class TestRetrieveAssetFile:

    def test_retrieve_asset_file_successfully(self, monkeypatch, registry):
        from adhocracy_core import utils
        from adhocracy_core.sheets.asset import IAssetData, retrieve_asset_file
        mock_sheet = Mock()
        mock_sheet.get.return_value = {'data': 'dummy'}
        mock_get_sheet = Mock(spec=utils.get_sheet, return_value=mock_sheet)
        monkeypatch.setattr(utils, 'get_sheet', mock_get_sheet)
        context = testing.DummyResource(__provides__=IAssetData)
        assert retrieve_asset_file(context, registry) == 'dummy'

    def test_retrieve_asset_file_missing_sheet(self, registry_with_content):
        from adhocracy_core.exceptions import RuntimeConfigurationError
        from adhocracy_core.sheets.asset import retrieve_asset_file
        context = testing.DummyResource()
        registry_with_content.content.get_sheet.side_effect =\
            RuntimeConfigurationError
        with raises(RuntimeConfigurationError):
            retrieve_asset_file(context, registry_with_content)
