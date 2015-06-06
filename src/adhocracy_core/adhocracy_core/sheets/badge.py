"""Badge sheet."""
import colander
from pyramid.request import Request
from pyramid.traversal import lineage
from substanced.util import find_service

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IPostPoolSheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.interfaces import search_query
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.schema import Reference
from adhocracy_core.schema import PostPoolMappingSchema
from adhocracy_core.schema import PostPool


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


class BadgeGroupReference(SheetToSheet):

    """Reference from badge to badge group."""

    source_isheet = IBadge
    source_isheet_field = 'groups'
    target_isheet = IPool  # TODO add special sheet for badge groups


@colander.deferred
def deferred_groups_default(node: colander.SchemaNode, kw: dict) -> []:
    from adhocracy_core.resources.badge import IBadgeGroup  # no circle imports
    context = kw.get('context', None)
    if context is None:
        return []
    parents = [x for x in lineage(context)][1:]
    groups = []
    for parent in parents:
        if IBadgeGroup.providedBy(parent):
            groups.append(parent)
        else:
            break
    return groups


class BadgeSchema(colander.MappingSchema):

    """Badge sheet data structure."""

    groups = UniqueReferences(reftype=BadgeGroupReference,
                              readonly=True,
                              default=deferred_groups_default,
                              )


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


def get_assignable_badges(context: IBadgeable, request: Request) -> [IBadge]:
    """Get assignable badges for the IBadgeAssignment sheet."""
    badges = find_service(context, 'badges')
    if badges is None:
        return []
    catalogs = find_service(context, 'catalogs')
    principals = request.effective_principals
    query = search_query._replace(root=badges,
                                  interfaces=IBadge,
                                  allows=(principals, 'assign_badge'),
                                  )
    result = catalogs.search(query)
    return result.elements


def includeme(config):
    """Register sheets, adapters and index views."""
    add_sheet_to_registry(badge_assignment_meta, config.registry)
    add_sheet_to_registry(badge_meta, config.registry)
    add_sheet_to_registry(badgeable_meta, config.registry)
    add_sheet_to_registry(can_badge_meta, config.registry)
    add_sheet_to_registry(has_badges_pool_meta, config.registry)
