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
        file = Mock()
        inst.resized = file
        assert inst.get_response(registry) == file.get_response.return_value

    def test_get_response_return_resized_image_if_dimensions_and_asset_parent(
            self, inst, asset, dimensions, mock_sheet, registry, monkeypatch):
        from . import image
        asset['download'] = inst
        inst.dimensions = dimensions
        file = Mock()
        mock_crop_and_resize = Mock(return_value=file)
        monkeypatch.setattr(image, 'crop_and_resize', mock_crop_and_resize)
        mock_sheet.get.return_value = {'data': file}
        assert inst.get_response(registry) == file.get_response.return_value
        mock_crop_and_resize.assert_called_with(file, dimensions)
        assert inst.resized is file

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


def test_crop_and_resize_image(monkeypatch, dimensions):
    from .image import crop_and_resize
    import io
    from PIL import Image
    from substanced.file import File
    blob = Mock()
    blob.open.return_value = io.BytesIO(b'dummy blob')
    file = Mock(spec=File, mimetype= 'image/png', blob=blob)
    mock_image = Mock(size=(840, 700))
    mock_crop = Mock()
    mock_image.crop.return_value = mock_crop
    mock_open = Mock(spec=Image.open, return_value=mock_image)
    monkeypatch.setattr(Image, 'open', mock_open)
    result = crop_and_resize(file, dimensions)
    assert isinstance(result, File)
    assert result.mimetype == file.mimetype
    assert mock_crop.resize.call_args[0] == (dimensions, Image.ANTIALIAS)


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
        assert meta.after_creation == (asset.add_metadata_and_download,
                                       image.add_image_size_downloads,
                                       )

    @mark.usefixtures('integration')
    def test_create(self, registry, meta, pool):
        from adhocracy_core.interfaces import Dimensions
        from adhocracy_core.sheets.asset import IAssetData
        from adhocracy_core.sheets.image import IImageMetadata
        from .image import IImageDownload
        from .asset import IAssetDownload
        from adhocracy_core.utils import get_sheet
        file = Mock(mimetype='image/png', size=100, title='title')
        appstructs = {IAssetData.__identifier__: {'data': file}}
        res = registry.content.create(meta.iresource.__identifier__,
                                      appstructs=appstructs,
                                      parent=pool)
        meta = get_sheet(res, IImageMetadata).get()
        assert meta['filename'] == 'title'
        assert meta['size'] == 100
        assert meta['raw'] == res['0000000']
        assert IAssetDownload.providedBy(meta['raw'])
        assert meta['detail'] == res['0000001']
        assert IImageDownload.providedBy(meta['detail'])
        assert res['0000001'].dimensions == Dimensions(height=800, width=800)
        assert meta['thumbnail'] == res['0000002']
        assert meta['thumbnail'].dimensions == Dimensions(height=100, width=100)

