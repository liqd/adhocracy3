"""image sheet."""
from colander import MappingSchema
from adhocracy_core.interfaces import Dimensions
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets.asset import IAssetMetadata
from adhocracy_core.sheets.asset import asset_metadata_meta
from adhocracy_core.schema import Reference
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet


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


class IImageReference(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for an image reference."""


class ImageReference(SheetToSheet):

    """Reference to an image."""

    source_isheet = IImageReference
    source_isheet_field = 'picture'
    target_isheet = IImageMetadata


class ImageReferenceSchema(MappingSchema):

    """Data structure for the image reference sheet."""

    picture = Reference(reftype=ImageReference)


image_reference_meta = asset_metadata_meta._replace(
    isheet=IImageReference,
    schema_class=ImageReferenceSchema,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(image_metadata_meta, config.registry)
    add_sheet_to_registry(image_reference_meta, config.registry)
