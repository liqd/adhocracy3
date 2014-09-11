"""Sheets to work with versionable resources."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_metadata_defaults
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.pool import PoolSheet
from adhocracy_core.schema import UniqueReferences


class ITag(ISheet):

    """Marker interface for the tag sheet."""


class TagElementsReference(SheetToSheet):

    """Tag sheet elements reference."""

    source_isheet = ITag
    source_isheet_field = 'elements'
    target_isheet = IVersionable


class TagSchema(colander.MappingSchema):

    """Tag sheet data structure.

    `elements`: Resources with this Tag
    """

    elements = UniqueReferences(reftype=TagElementsReference)


tag_metadata = sheet_metadata_defaults._replace(isheet=ITag,
                                                schema_class=TagSchema,
                                                )


class ITags(ISheet):

    """Marker interface for the tag sheet."""


class TagsElementsReference(SheetToSheet):

    """Tags sheet elements reference."""

    source_isheet = ITags
    source_isheet_field = 'elements'
    target_isheet = ITag


class TagsSchema(colander.MappingSchema):

    """Tags sheet data structure.

    `elements`: Tags in this Pool
    """

    elements = UniqueReferences(reftype=TagsElementsReference)


tags_metadata = sheet_metadata_defaults._replace(isheet=ITags,
                                                 schema_class=TagsSchema,
                                                 sheet_class=PoolSheet,
                                                 editable=False,
                                                 creatable=False,
                                                 )


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(tag_metadata, config.registry)
    add_sheet_to_registry(tags_metadata, config.registry)
