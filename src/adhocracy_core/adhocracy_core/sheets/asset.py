"""Sheets for managing assets."""

from colander import required
from colander import deferred
from persistent import Persistent
from zope.deprecation import deprecated

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import FileStore
from adhocracy_core.schema import Integer
from adhocracy_core.schema import PostPool
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import SchemaNode
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.utils import get_iresource


# check python-magic is installed properly to make mime type validation work
import magic  # noqa


class IHasAssetPool(ISheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for resources that have an asset pool."""


class HasAssetPoolSchema(MappingSchema):
    """Data structure pointing to an asset pool."""

    asset_pool = PostPool(iresource_or_service_name='assets')


has_asset_pool_meta = sheet_meta._replace(
    isheet=IHasAssetPool,
    schema_class=HasAssetPoolSchema,
    editable=False,
    creatable=False,
)


class IAssetMetadata(ISheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for asset metadata."""


class AssetReference(SheetToSheet):
    """Reference to an asset."""

    target_isheet = IAssetMetadata


class AssetMetadataSchema(MappingSchema):
    """Data structure storing asset metadata."""

    mime_type = SingleLine(readonly=True)
    size = Integer(readonly=True)
    filename = SingleLine(readonly=True)
    attached_to = UniqueReferences(readonly=True,
                                   backref=True,
                                   reftype=AssetReference)


asset_metadata_meta = sheet_meta._replace(
    isheet=IAssetMetadata,
    schema_class=AssetMetadataSchema,
)


class IAssetData(ISheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for the actual asset data."""


@deferred
def deferred_validate_asset_mime_type(node: SchemaNode, kw: dict):
    """Validate mime type for the uploaded asset file data."""
    from .image import validate_image_data_mimetype
    from adhocracy_core.resources.image import IImage
    context = kw['context']
    creating = kw['creating']
    iresource = creating and creating.iresource or get_iresource(context)
    is_image = iresource.isOrExtends(IImage)
    if is_image:
        return validate_image_data_mimetype


class AssetDataSchema(MappingSchema):
    """Data structure storing for the actual asset data."""

    data = FileStore(missing=required,
                     validator=deferred_validate_asset_mime_type)


asset_data_meta = sheet_meta._replace(
    isheet=IAssetData,
    schema_class=AssetDataSchema,
    readable=False,
)


class AssetFileDownload(Persistent):
    """Wrapper for a File object that allows downloading the asset data."""


deprecated('IAssetFileDownload', 'Use .resources.assets.AssetDownload instead')


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(has_asset_pool_meta, config.registry)
    add_sheet_to_registry(asset_metadata_meta, config.registry)
    add_sheet_to_registry(asset_data_meta, config.registry)
