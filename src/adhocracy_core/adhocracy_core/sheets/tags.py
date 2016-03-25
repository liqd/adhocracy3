"""Sheets for tagging."""
from logging import getLogger
from zope.deprecation import deprecated

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Reference


logger = getLogger(__name__)


class ITag(ISheet):
    """Marker interface for the tag sheet."""
deprecated('ITag', 'Not needed anymore')


class TagElementsReference(SheetToSheet):
    """Tag sheet elements reference."""

    source_isheet = ITag
    source_isheet_field = 'elements'
    target_isheet = IVersionable

deprecated('TagElementsReference',
           'Use adhocracy_core.sheets.tags.TagsFirst/LastReference instead')


class ITags(ISheet):
    """Marker interface for the tags sheet."""


class TagsFirstReference(SheetToSheet):
    """Tags sheet first reference."""

    source_isheet = ITags
    source_isheet_field = 'FIRST'
    target_isheet = IVersionable


class TagsLastReference(SheetToSheet):
    """Tags sheet last reference."""

    source_isheet = ITags
    source_isheet_field = 'LAST'
    target_isheet = IVersionable


class TagsSchema(MappingSchema):
    """Tags sheet data structure."""

    LAST = Reference(reftype=TagsLastReference)
    FIRST = Reference(reftype=TagsFirstReference)


tags_meta = sheet_meta._replace(isheet=ITags,
                                schema_class=TagsSchema,
                                editable=False,
                                creatable=False,
                                )


def includeme(config):
    """Register tags sheet."""
    add_sheet_to_registry(tags_meta, config.registry)
