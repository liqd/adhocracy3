"""Sheets for tagging."""
from logging import getLogger

import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.pool import PoolSheet
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.utils import find_graph


logger = getLogger(__name__)


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


tag_meta = sheet_meta._replace(isheet=ITag,
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


tags_meta = sheet_meta._replace(isheet=ITags,
                                schema_class=TagsSchema,
                                sheet_class=PoolSheet,
                                editable=False,
                                creatable=False,
                                )


def filter_by_tag(resources: list, tag_name: str) -> list:
    """Filter a list of resources by returning only those with a given tag."""
    result = []
    if not resources:
        return result
    graph = find_graph(resources[0])
    for resource in resources:
        tags = graph.get_back_reference_sources(resource, TagElementsReference)
        for tag in tags:
            if tag.__name__ == tag_name:
                result.append(resource)
                break
    return result


def includeme(config):
    """Register sheets and add indexviews."""
    add_sheet_to_registry(tag_meta, config.registry)
    add_sheet_to_registry(tags_meta, config.registry)
