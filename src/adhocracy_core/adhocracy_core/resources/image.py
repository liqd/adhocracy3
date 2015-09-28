"""image resource type."""
import io

from pyramid.response import FileResponse
from pyramid.registry import Registry
from substanced.file import File
import transaction
from PIL import Image

from adhocracy_core.interfaces import Dimensions
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.asset import IAsset
from adhocracy_core.resources.asset import IAssetDownload
from adhocracy_core.resources.asset import AssetDownload
from adhocracy_core.resources.asset import asset_download_meta
from adhocracy_core.resources.asset import asset_meta
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_matching_isheet
import adhocracy_core.sheets.image


class IImageDownload(IAssetDownload):

    """Downloadable binary file for Images."""


class ImageDownload(AssetDownload):

    """Allow downloading the first image file in the term:`lineage`."""

    dimensions = None
    """:class:`adhocracy_core.interfaces.Dimension` to resize the image"""
    resized = None
    """Resized  image :class:`substanced.file.File`."""

    def get_response(self, registry: Registry=None) -> FileResponse:
        """Return response with resized binary content of the image data."""
        if self.resized:
            return self.resized.get_response()
        original = self._get_asset_file_in_lineage(registry)
        if self.dimensions:
            self.resized = crop_and_resize(original, self.dimensions)
            transaction.commit()  # to avoid BlobError: Uncommitted changes
            return self.resized.get_response()
        else:
            return original.get_response()


def crop_and_resize(original: File, dimensions: Dimensions) -> File:
    """"Crop and resize `file` image with mod:`PIL`."""
    with original.blob.open('r') as blobdata:
        mimetype = original.mimetype
        image = Image.open(blobdata)
        cropped = crop(image, dimensions)
        resized = cropped.resize(dimensions, Image.ANTIALIAS)
        bytestream = io.BytesIO()
        resized.save(bytestream, image.format)
        bytestream.seek(0)
    return File(stream=bytestream, mimetype=mimetype)


def crop(image: Image, dimensions: Dimensions) -> Image:
    """Return a cropped version of `image`.

    The returned version will have the same aspect ratio as the target
    dimensions, but not necessarily the same size, so a further resizing
    step may be needed. If the original image is wider, it is cropped in
    X direction so that only the middle part remains. If it's higher, it's
    cropped in Y direction.

    If original and target aspect ratio are identical, the image is
    returned unchanged.
    """
    original_aspect_ratio = image.size[0] / image.size[1]
    target_aspect_ratio = dimensions.width / dimensions.height
    if target_aspect_ratio > original_aspect_ratio:
        # height must be cropped
        cropped_height = round(image.size[0] / target_aspect_ratio)
        if cropped_height == image.size[1]:
            return image  # No cropping necessary
        upper = round((image.size[1] - cropped_height) / 2)
        #          (left, upper, right,      lower)
        crop_box = (0, upper, image.size[0], upper + cropped_height)
    else:
        # width must be cropped
        cropped_width = round(image.size[1] * target_aspect_ratio)
        if cropped_width == image.size[0]:
            return image  # No cropping necessary
        left = round((image.size[0] - cropped_width) / 2)
        #          (left, upper, right,            lower)
        crop_box = (left, 0, left + cropped_width, image.size[1])
    return image.crop(crop_box)


image_download_meta = asset_download_meta._replace(
    content_name='ImageDownload',
    iresource=IImageDownload,
    use_autonaming=True,
    content_class=ImageDownload,
)


class IImage(IAsset):

    """An image asset."""


def add_image_size_downloads(context: IImage, registry: Registry, **kwargs):
    """Add download for every image size of `context`."""
    isheet = get_matching_isheet(context,
                                 adhocracy_core.sheets.image.IImageMetadata)
    sheet = get_sheet(context, isheet, registry=registry)
    size_fields = (f for f in sheet.schema if hasattr(f, 'dimensions'))
    appstruct = {}
    for field in size_fields:
        download = registry.content.create(IImageDownload.__identifier__,
                                           parent=context)
        download.dimensions = field.dimensions
        appstruct[field.name] = download
    sheet.set(appstruct, omit_readonly=False)


image_meta = asset_meta._replace(
    iresource=IImage,
    is_implicit_addable=True,
    extended_sheets=(adhocracy_core.sheets.image.IImageMetadata,),
)._add(after_creation=(add_image_size_downloads,))


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(image_meta, config)
    add_resource_type_to_registry(image_download_meta, config)
