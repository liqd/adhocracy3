"""image sheet."""

from adhocracy_core.interfaces import Dimensions
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets.asset import IAssetMetadata
from adhocracy_core.sheets.asset import asset_metadata_meta


class IImageMetadata(IAssetMetadata):

    """Marker interface for images."""


def image_mime_type_validator(mime_type: str) -> bool:
    """Validate image file types."""
    return mime_type in ('image/gif', 'image/jpeg', 'image/png')


image_metadata_meta = asset_metadata_meta._replace(
    isheet=IImageMetadata,
    mime_type_validator=image_mime_type_validator,
    image_sizes={'thumbnail': Dimensions(width=100, height=100),
                 'detail': Dimensions(width=800, height=800)},
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(image_metadata_meta, config.registry)
