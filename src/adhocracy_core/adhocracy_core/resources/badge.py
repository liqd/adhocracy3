"""Resources for managing badges."""

from pyramid.registry import Registry

from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.interfaces import ISimple
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import pool_meta
from adhocracy_core.resources.service import service_meta
import adhocracy_core.sheets.metadata
import adhocracy_core.sheets.title
import adhocracy_core.sheets.name
import adhocracy_core.sheets.badge


class IBadge(ISimple):

    """A generic badge."""


badge_meta = pool_meta._replace(
    iresource=IBadge,
    basic_sheets=[
        adhocracy_core.sheets.metadata.IMetadata,
        adhocracy_core.sheets.name.IName,
        adhocracy_core.sheets.badge.IBadgeAssignments,
        adhocracy_core.sheets.badge.IBadgeData,
    ],
    permission_create='create_badge',
)


class IBadgesService(IServicePool):

    """The 'badges' ServicePool."""


badges_service_meta = service_meta._replace(
    iresource=IBadgesService,
    content_name='badges',
    element_types=[IBadge],
)


def add_badges_service(context: IPool, registry: Registry, options: dict):
    """Add `badges` service to context."""
    registry.content.create(IBadgesService.__identifier__, parent=context)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(badge_meta, config)
    add_resource_type_to_registry(badges_service_meta, config)
