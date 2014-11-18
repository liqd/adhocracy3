"""Sheets for managing assets."""

import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.schema import Reference
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_metadata_defaults
from adhocracy_core.sheets.pool import FilteringPoolSheet


class IHasAssetPool(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for resources that have an asset pool."""


class AssetPoolReference(SheetToSheet):

    """Reference to an asset pool."""

    source_isheet = IHasAssetPool
    source_isheet_field = 'asset_pool'
    target_isheet = FilteringPoolSheet


class HasAssetPoolSchema(colander.MappingSchema):

    """Commentable sheet data structure.

    `comments`: list of comments (not stored)
    `post_pool`: Pool to post new :class:`adhocracy_sample.resource.IComment`.
    """

    asset_pool = Reference(reftype=AssetPoolReference)


has_asset_pool_meta = sheet_metadata_defaults._replace(
    isheet=IHasAssetPool,
    schema_class=HasAssetPoolSchema,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(has_asset_pool_meta, config.registry)
