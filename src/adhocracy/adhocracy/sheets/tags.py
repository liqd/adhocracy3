"""Sheets to work with versionable resources."""
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets.versions import IVersionable
from adhocracy.sheets.pool import PoolSheet
from adhocracy.schema import ListOfUniqueReferences


class ITag(ISheet):

    """Marker interface for the tag sheet."""


class ITagElementsReference(SheetToSheet):

    """Tag sheet elements reference."""

    source_isheet = ITag
    source_isheet_field = 'elements'
    target_isheet = IVersionable


class TagSchema(colander.MappingSchema):

    """Tag sheet data structure.

    `elements`: Resources with this Tag

    """

    elements = ListOfUniqueReferences(reftype=ITagElementsReference)


tag_metadata = sheet_metadata_defaults._replace(isheet=ITag,
                                                schema_class=TagSchema,
                                                )


class ITags(ISheet):

    """Marker interface for the tag sheet."""


class ITagsElementsReference(SheetToSheet):

    """Tags sheet elements reference."""

    source_isheet = ITags
    source_isheet_field = 'elements'
    target_isheet = ITag


class TagsSchema(colander.MappingSchema):

    """Tags sheet data structure.

    `elements`: Tags in this Pool

    """

    elements = ListOfUniqueReferences(
        reftype=ITagsElementsReference)


tags_metadata = sheet_metadata_defaults._replace(isheet=ITags,
                                                 schema_class=TagsSchema,
                                                 sheet_class=PoolSheet,
                                                 )


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(tag_metadata, config.registry)
    add_sheet_to_registry(tags_metadata, config.registry)
