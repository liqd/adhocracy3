"""Badge sheet."""
from colander import deferred
from colander import All
from colander import Invalid
from pyramid.request import Request
from pyramid.traversal import lineage
from pyramid.traversal import resource_path
from substanced.util import find_service

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.interfaces import search_query
from adhocracy_core.schema import SchemaNode
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import PostPool
from adhocracy_core.schema import Reference
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.schema import create_post_pool_validator
from adhocracy_core.schema import validate_reftype
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets.name import IName
from adhocracy_core.sheets.pool import IPool


class IBadge(ISheet):
    """Marker interface for badge data sheet."""


class IHasBadgesPool(ISheet):
    """Marker interface for resources that have a badge datas pool."""


class ICanBadge(ISheet):
    """Marker interface for principals that can assign badges."""


class IBadgeable(ISheet):
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


@deferred
def deferred_groups_default(node: SchemaNode, kw: dict) -> []:
    """Return badge groups."""
    from adhocracy_core.resources.badge import IBadgeGroup  # no circle imports
    context = kw['context']
    parents = [x for x in lineage(context)][1:]
    groups = []
    for parent in parents:
        if IBadgeGroup.providedBy(parent):
            groups.append(parent)
        else:
            break
    return groups


class BadgeSchema(MappingSchema):
    """Badge sheet data structure."""

    groups = UniqueReferences(reftype=BadgeGroupReference,
                              readonly=True,
                              default=deferred_groups_default,
                              )


badge_meta = sheet_meta._replace(isheet=IBadge,
                                 schema_class=BadgeSchema,
                                 )


class HasBadgesPoolSchema(MappingSchema):
    """Data structure pointing to a badges post pool."""

    badges_pool = PostPool(iresource_or_service_name='badges')


has_badges_pool_meta = sheet_meta._replace(
    isheet=IHasBadgesPool,
    schema_class=HasBadgesPoolSchema,
    editable=False,
    creatable=False,
)


class CanBadgeSchema(MappingSchema):
    """CanBadge sheet data structure."""


can_badge_meta = sheet_meta._replace(
    isheet=ICanBadge,
    schema_class=CanBadgeSchema,
    editable=False,
    creatable=False,
)


class BadgeableSchema(MappingSchema):
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


def create_unique_badge_assignment_validator(badge_ref: Reference,
                                             object_ref: Reference,
                                             kw: dict) -> callable:
    """Create validator to check that a badge assignment is unique.

    Badge assignments is considered unique if there is at most one for each
    badge in :term:`post_pool`.

    :param badge: Reference to a sheet with :term:`post_pool` field.
    :param kw: dictionary with keys `context` and `registry`.
    """
    context = kw['context']
    registry = kw['registry']

    def validator(node, value):
        new_badge = node.get_value(value, badge_ref.name)
        new_badge_name = registry.content.get_sheet_field(new_badge,
                                                          IName,
                                                          'name')
        new_object = node.get_value(value, object_ref.name)
        pool = find_service(context, 'badge_assignments')
        for badge_assignment in pool.values():
            badge_sheet_values = registry.content.get_sheet(
                badge_assignment,
                IBadgeAssignment).get()
            badge = badge_sheet_values['badge']
            badge_name = registry.content.get_sheet_field(badge,
                                                          IName,
                                                          'name')
            obj = badge_sheet_values['object']
            updating_current_assignment = context == badge_assignment
            if new_badge_name == badge_name \
               and new_object == obj \
               and not updating_current_assignment:
                raise Invalid(badge_ref, 'Badge already assigned')

    return validator


@deferred
def deferred_validate_badge(node, kw):
    """Check `assign_badge` permission and ISheet interface of `badge` node."""
    request = kw['request']

    def check_assign_badge_permisson(node, value):
        if not request.has_permission('assign_badge', value):
            badge_path = resource_path(value)
            raise Invalid(node, 'Your are missing the `assign_badge` '
                                ' permission for: ' + badge_path)
    return All(validate_reftype,
               check_assign_badge_permisson,
               )


class BadgeAssignmentSchema(MappingSchema):
    """Badge sheet data structure."""

    subject = Reference(reftype=BadgeSubjectReference)
    badge = Reference(reftype=BadgeReference,
                      validator=deferred_validate_badge
                      )
    object = Reference(reftype=BadgeObjectReference)

    @deferred
    def validator(self, kw: dict) -> callable:
        """Validate the :term:`post_pool` for the object reference."""
        object_validator = create_post_pool_validator(self['object'], kw)
        badge_assignment_validator = create_unique_badge_assignment_validator(
            self['badge'], self['object'], kw)
        return All(object_validator, badge_assignment_validator)


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
    query = search_query._replace(root=badges,
                                  interfaces=IBadge,
                                  allows=(request.effective_principals,
                                          'assign_badge'),
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
