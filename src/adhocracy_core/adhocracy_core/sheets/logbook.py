"""Logbook sheet."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import PostPool


class IHasLogbookPool(ISheet):

    """Marker interface for resources that have a logbook pool."""


class HasLogbookPoolSchema(colander.MappingSchema):

    """Data structure pointing to a logbook pool."""

    logbook_pool = PostPool(iresource_or_service_name='logbook')


has_logbook_pool_meta = sheet_meta._replace(
    isheet=IHasLogbookPool,
    schema_class=HasLogbookPoolSchema,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheets, adapters and index views."""
    add_sheet_to_registry(has_logbook_pool_meta, config.registry)
