from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


@fixture
def dimensions():
    from adhocracy_core.interfaces import Dimensions
    return Dimensions(width=200, height=100)


class TestImageDownload:

    @fixture
    def registry(self, registry_with_content, mock_sheet):
        registry = registry_with_content
        registry.content.get_sheet.return_value = mock_sheet
        return registry

    @fixture
    def meta(self):
        from .image import image_download_meta
        return image_download_meta

    @fixture
    def asset(self):
      from adhocracy_core.sheets.asset import IAssetData
      return testing.DummyResource(__provides__=IAssetData)

    @fixture
    def inst(self, meta):
        inst = meta.content_class()
        return inst

    def test_meta(self, meta):
        from . import image
        from . import asset
        assert meta.iresource is image.IImageDownload
        assert meta.iresource.isOrExtends(asset.IAssetDownload)
        assert meta.content_class == image.ImageDownload
        assert issubclass(meta.content_class, asset.AssetDownload)
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

    def test_get_response_return_old_resized_image(self, inst, registry):
        inst._is_resized = Mock(return_value=True)
        inst._get_response = Mock(return_value='FileResponse')
        response = inst.get_response(registry)
        assert response is inst._get_response.return_value

    def test_is_resized_return_true_if_blob_has_size(self, inst):
        inst.get_size = Mock(return_value=100)
        assert inst._is_resized()

    def test_is_resized_return_false_if_blob_no_size(self, inst):
        inst.get_size = Mock(return_value=0)
        assert not inst._is_resized()

    def test_is_resized_return_false_if_blob_raises_error(self, inst):
        from ZODB.blob import BlobError
        inst.get_size = Mock(side_effect=BlobError)
        assert not inst._is_resized()

    def test_get_response_return_resized_image_if_dimensions_and_asset_parent(
            self, inst, asset, dimensions, mock_sheet, registry):
        asset['download'] = inst
        original = Mock()
        mock_sheet.get.return_value = {'data': original}
        inst._upload_crop_and_resize = Mock()
        inst.dimensions = dimensions
        inst._get_response = Mock(return_value='FileResponse')
        response = inst.get_response(registry)
        assert response is inst._get_response.return_value
        inst._upload_crop_and_resize.assert_called_with(original)

    def test_upload_crop_and_resize(self, inst, monkeypatch, dimensions):
        import io
        from PIL import Image
        from substanced.file import File
        blob = Mock()
        blob.open.return_value = io.BytesIO(b'dummy blob')
        original = Mock(spec=File, mimetype= 'image/png', blob=blob)
        mock_image = Mock(size=(840, 700))
        mock_crop = Mock()
        mock_image.crop.return_value = mock_crop
        mock_open = Mock(spec=Image.open, return_value=mock_image)
        monkeypatch.setattr(Image, 'open', mock_open)
        inst.upload = Mock()
        inst.dimensions = dimensions
        inst._upload_crop_and_resize(original)
        assert inst.mimetype == original.mimetype
        assert mock_crop.resize.call_args[0] == (dimensions, Image.ANTIALIAS)
        resized = inst.upload.call_args[0][0]
        assert isinstance(resized, io.BytesIO)

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)



class TestCrop:

    def call_fut(self, *args):
        from .image import crop
        return crop(*args)

    def test_crop_height(self, dimensions):
        mock_image = Mock(size=(840, 700))
        crop_result = Mock()
        mock_image.crop.return_value = crop_result
        assert self.call_fut(mock_image, dimensions) == crop_result
        assert mock_image.crop.call_args[0][0] == (0, 140, 840, 560)

    def test_crop_width(self, dimensions):
        mock_image = Mock(size=(1000, 400))
        crop_result = Mock()
        mock_image.crop.return_value = crop_result
        assert self.call_fut(mock_image, dimensions) == crop_result
        assert mock_image.crop.call_args[0][0] == (100, 0, 900, 400)

    def test_crop_no_cropping_needed(self, dimensions):
        mock_image = Mock(size=(800, 400))
        assert self.call_fut(mock_image, dimensions) == mock_image
        assert not mock_image.crop.called

    def test_crop_no_cropping_needed_due_to_rounding(self, dimensions):
        mock_image = Mock(size=(999, 500))
        assert self.call_fut(mock_image, dimensions) == mock_image
        assert not mock_image.crop.called


class TestImage:

    @fixture
    def meta(self):
        from .image import image_meta
        return image_meta

    def test_meta(self, meta):
        from . import image
        from . import asset
        import adhocracy_core.sheets.image
        assert meta.iresource is image.IImage
        assert meta.is_implicit_addable is True
        assert meta.extended_sheets ==\
               (adhocracy_core.sheets.image.IImageMetadata,)
        assert meta.after_creation == (asset.add_metadata,
                                       image.add_image_size_downloads,
                                       )

    @mark.usefixtures('integration')
    def test_create(self, registry, meta, pool):
        from adhocracy_core.interfaces import Dimensions
        from adhocracy_core.sheets.asset import IAssetData
        from adhocracy_core.sheets.image import IImageMetadata
        from .image import IImageDownload
        from adhocracy_core.utils import get_sheet
        file = Mock(mimetype='image/png', size=100, title='title')
        appstructs = {IAssetData.__identifier__: {'data': file}}
        res = registry.content.create(meta.iresource.__identifier__,
                                      appstructs=appstructs,
                                      parent=pool)
        meta = get_sheet(res, IImageMetadata).get()
        assert meta['filename'] == 'title'
        assert meta['size'] == 100
        assert meta['detail'] == res['0000000']
        assert IImageDownload.providedBy(meta['detail'])
        assert meta['detail'].dimensions == Dimensions(height=800, width=800)
        assert meta['thumbnail'] == res['0000001']
        assert meta['thumbnail'].dimensions == Dimensions(height=100, width=100)

