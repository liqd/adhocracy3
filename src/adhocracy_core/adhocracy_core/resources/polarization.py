"""Polarization resource type."""
from pyramid.registry import Registry

from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_meta
from adhocracy_core.resources.item import item_meta
from adhocracy_core.resources.service import service_meta

import adhocracy_core.sheets.polarization
import adhocracy_core.sheets.comment


class IPolarizationVersion(IItemVersion):

    """A polarization in a discussion."""


polarizationversion_meta = itemversion_meta._replace(
    content_name='PolarizationVersion',
    iresource=IPolarizationVersion,
    extended_sheets=(adhocracy_core.sheets.polarization.IPolarization,
                     adhocracy_core.sheets.comment.ICommentable,
                     ),
    permission_create='edit_comment',
)


class IPolarization(IItem):

    """Polarization versions pool."""


polarization_meta = item_meta._replace(
    content_name='Polarization',
    iresource=IPolarization,
    element_types=(IPolarizationVersion,
                   ),
    item_type=IPolarizationVersion,
    use_autonaming=True,
    autonaming_prefix='polarization_',
    permission_create='create_comment',
)


class IPolarizationsService(IServicePool):

    """The 'polarizations' ServicePool."""


polarizations_meta = service_meta._replace(
    iresource=IPolarizationsService,
    content_name='polarizations',
    element_types=(IPolarization,),
)


def add_polarizationsservice(context: IPool,
                             registry: Registry,
                             options: dict):
    """Add `polarizations` service to context."""
    registry.content.create(IPolarizationsService.__identifier__,
                            parent=context)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(polarizations_meta, config)
    add_resource_type_to_registry(polarizationversion_meta, config)
    add_resource_type_to_registry(polarization_meta, config)
