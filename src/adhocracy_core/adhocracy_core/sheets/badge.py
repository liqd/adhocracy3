"""Badge sheet."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IPostPoolSheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import PostPoolMappingSchema
from adhocracy_core.schema import PostPool
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text


class IBadgeAssignments(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the badge assignments sheet."""


class IBadgeable(IPostPoolSheet):

    """Marker interface for resources that can be badged."""


class BadgeReference(SheetToSheet):

    """Reference from badge to badged resource."""

    source_isheet = IBadgeAssignments
    source_isheet_field = 'badges'
    target_isheet = IBadgeable


class BadgeAssignmentsSchema(colander.MappingSchema):

    """Badge sheet data structure."""

    badges = UniqueReferences(reftype=BadgeReference)


badge_assignments_meta = sheet_meta._replace(
    isheet=IBadgeAssignments,
    schema_class=BadgeAssignmentsSchema,
    permission_edit='edit_sheet_badge_assignments'
    )


class IBadgeData(IPostPoolSheet):

    """Marker interface for badge data sheet."""


class BadgeDataSchema(colander.MappingSchema):

    """Badge sheet data structure."""

    title = SingleLine()
    description = Text()
    color = SingleLine()


badge_data_meta = sheet_meta._replace(isheet=IBadgeData,
                                      schema_class=BadgeDataSchema,
                                      permission_edit='edit_sheet_badge_data'
                                      )



class IHasBadgesPool(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for resources that have an badge pool."""


class HasBadgesPoolSchema(colander.MappingSchema):

    """Data structure pointing to an badge pool."""

    badges_pool = PostPool(iresource_or_service_name='badges')


has_badges_pool_meta = sheet_meta._replace(
    isheet=IHasBadgesPool,
    schema_class=HasBadgesPoolSchema,
    editable=False,
    creatable=False,
)


class BadgeableSchema(PostPoolMappingSchema):

    """Commentable sheet data structure.

    `post_pool`: Pool to post new :class:`adhocracy_sample.resource.IBadgeAssignments`.
    """

    badged_by = UniqueReferences(readonly=True,
                                 backref=True,
                                 reftype=BadgeReference)
    post_pool = PostPool(iresource_or_service_name='badges')


badgeable_meta = sheet_meta._replace(
    isheet=IBadgeable,
    schema_class=BadgeableSchema,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheets, adapters and index views."""
    add_sheet_to_registry(badge_assignments_meta, config.registry)
    add_sheet_to_registry(badge_data_meta, config.registry)
    add_sheet_to_registry(badgeable_meta, config.registry)
    add_sheet_to_registry(has_badges_pool_meta, config.registry)
