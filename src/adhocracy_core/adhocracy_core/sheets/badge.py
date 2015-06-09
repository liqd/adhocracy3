"""Badge sheet."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IPostPoolSheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.schema import Reference
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import PostPoolMappingSchema
from adhocracy_core.schema import PostPool
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text


class IBadge(IPostPoolSheet):

    """Marker interface for badge data sheet."""


class IHasBadgesPool(ISheet):

    """Marker interface for resources that have a badge datas pool."""


class ICanBadge(ISheet):

    """Marker interface for principals that can assign badges."""


class IBadgeable(IPostPoolSheet):

    """Marker interface for resources that can be badged."""


class IBadgeAssignment(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the badge assignment sheet."""


class BadgeReference(SheetToSheet):

    """Reference from badge to badge data resource."""

    source_isheet = IBadgeAssignment
    source_isheet_field = 'badge'
    target_isheet = IBadge


class BadgeSubjectReference(SheetToSheet):

    """Reference from badge to assigning user."""

    source_isheet = IBadgeAssignment
    source_isheet_field = 'subject'
    target_isheet = ICanBadge


class BadgeObjectReference(SheetToSheet):

    """Reference from badge to badged content."""

    source_isheet = IBadgeAssignment
    source_isheet_field = 'object'
    target_isheet = IBadgeable


class BadgeSchema(colander.MappingSchema):

    """Badge sheet data structure."""

    title = SingleLine()
    description = Text()
    color = SingleLine()


badge_meta = sheet_meta._replace(isheet=IBadge,
                                 schema_class=BadgeSchema,
                                 )


class HasBadgesPoolSchema(colander.MappingSchema):

    """Data structure pointing to a badges post pool."""

    badges_pool = PostPool(iresource_or_service_name='badges')


has_badges_pool_meta = sheet_meta._replace(
    isheet=IHasBadgesPool,
    schema_class=HasBadgesPoolSchema,
    editable=False,
    creatable=False,
)


class CanBadgeSchema(colander.MappingSchema):

    """CanBadge sheet data structure."""


can_badge_meta = sheet_meta._replace(
    isheet=ICanBadge,
    schema_class=CanBadgeSchema,
    editable=False,
    creatable=False,
)


class BadgeableSchema(PostPoolMappingSchema):

    """Badgeable sheet data structure.

    `post_pool`: Pool to post new
                 :class:`adhocracy_sample.resource.IBadgeAssignment`.
    """

    assignments = UniqueReferences(readonly=True,
                                   backref=True,
                                   reftype=BadgeObjectReference)
    post_pool = PostPool(iresource_or_service_name='badge_assignments')


badgeable_meta = sheet_meta._replace(
    isheet=IBadgeable,
    schema_class=BadgeableSchema,
    editable=False,
    creatable=False,
)


class BadgeAssignmentSchema(colander.MappingSchema):

    """Badge sheet data structure."""

    subject = Reference(reftype=BadgeSubjectReference)
    badge = Reference(reftype=BadgeReference)
    object = Reference(reftype=BadgeObjectReference)


badge_assignment_meta = sheet_meta._replace(
    isheet=IBadgeAssignment,
    schema_class=BadgeAssignmentSchema,
)


def includeme(config):
    """Register sheets, adapters and index views."""
    add_sheet_to_registry(badge_assignment_meta, config.registry)
    add_sheet_to_registry(badge_meta, config.registry)
    add_sheet_to_registry(badgeable_meta, config.registry)
    add_sheet_to_registry(can_badge_meta, config.registry)
    add_sheet_to_registry(has_badges_pool_meta, config.registry)
