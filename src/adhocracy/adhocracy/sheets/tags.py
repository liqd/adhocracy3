"""Sheets for tagging."""
from logging import getLogger

from pyramid.traversal import resource_path
from substanced.catalog import indexview
from substanced.catalog import indexview_defaults
from substanced.util import find_catalog
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.sheets import GenericResourceSheet
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets.versions import IVersionable
from adhocracy.sheets.pool import PoolSheet
from adhocracy.schema import UniqueReferences
from adhocracy.utils import find_graph


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


class TagSheet(GenericResourceSheet):

    """Resource sheet for a tag."""

    def set(self, appstruct: dict, omit=(), send_event=True) -> bool:
        """Store appstruct, updating the catalog."""
        old_element_set = set(self._get_references().get('elements', []))
        new_element_set = set(appstruct.get('elements', []))
        newly_tagged_or_untagged_resources = old_element_set ^ new_element_set
        result = super().set(appstruct, omit, send_event)

        if newly_tagged_or_untagged_resources:
            adhocracy_catalog = find_catalog(self.context, 'adhocracy')
            for resource in newly_tagged_or_untagged_resources:
                adhocracy_catalog.reindex_resource(resource)

        return result


tag_metadata = sheet_metadata_defaults._replace(isheet=ITag,
                                                schema_class=TagSchema,
                                                sheet_class=TagSheet
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


@indexview_defaults(catalog_name='adhocracy')
class VersionsCatalogViews(object):

    def __init__(self, resource):
        self.resource = resource

    @indexview()
    def tag(self, default):
        if IVersionable.providedBy(self.resource):
            graph = find_graph(self.resource)
            if graph is None:
                logger.warning(
                    'Cannot update tag index: No graph found for %s',
                    resource_path(self.resource))
                return default
            tags = graph.get_back_reference_sources(self.resource,
                                                    TagElementsReference)
            tagnames = [tag.__name__ for tag in tags]
            return tagnames if tagnames else default
        else:
            return default


def includeme(config):
    """Register sheets and scan indexview."""
    add_sheet_to_registry(tag_metadata, config.registry)
    add_sheet_to_registry(tags_metadata, config.registry)
    config.scan('.')
