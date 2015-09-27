"""image resource type."""

from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.asset import asset_meta
from adhocracy_core.resources.asset import IAsset
import adhocracy_core.sheets.image


class IImage(IAsset):

    """An image asset."""


image_meta = asset_meta._replace(
    iresource=IImage,
    is_implicit_addable=True,
    extended_sheets=(adhocracy_core.sheets.image.IImageMetadata,),
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(image_meta, config)
