"""Sheets for managing assets."""

import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.schema import FileStore
from adhocracy_core.schema import Integer
from adhocracy_core.schema import PostPool
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_metadata_defaults


class IHasAssetPool(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for resources that have an asset pool."""


class HasAssetPoolSchema(colander.MappingSchema):

    """Data structure pointing to an asset pool."""

    asset_pool = PostPool(iresource_or_service_name='assets')


has_asset_pool_meta = sheet_metadata_defaults._replace(
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


class AssetMetadataSchema(colander.MappingSchema):

    """Data structure storing asset metadata."""

    mime_type = SingleLine(missing=colander.required)
    size = Integer(readonly=True)
    filename = SingleLine(readonly=True)
    attached_to = UniqueReferences(readonly=True,
                                   backref=True,
                                   reftype=AssetReference)


asset_metadata_meta = sheet_metadata_defaults._replace(
    isheet=IAssetMetadata,
    schema_class=AssetMetadataSchema,
)


class IAssetData(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the actual asset data."""


class AssetDataSchema(colander.MappingSchema):

    """Data structure storing for the actual asset data."""

    data = FileStore(missing=colander.required)


asset_data_meta = sheet_metadata_defaults._replace(
    isheet=IAssetData,
    schema_class=AssetDataSchema,
    readable=False,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(has_asset_pool_meta, config.registry)
    add_sheet_to_registry(asset_metadata_meta, config.registry)
    add_sheet_to_registry(asset_data_meta, config.registry)
