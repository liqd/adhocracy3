"""Statements about relations between process content/comments."""
from pyramid.registry import Registry

from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_meta
from adhocracy_core.resources.item import item_meta
from adhocracy_core.resources.service import service_meta

import adhocracy_core.sheets.relation
import adhocracy_core.sheets.comment


class IRelation(IItem):

    """Relation versions pool."""


class IRelationVersion(IItemVersion):

    """Relation version."""


class IPolarizationVersion(IRelationVersion):

    """A polarization in a discussion."""


polarizationversion_meta = itemversion_meta._replace(
    content_name='PolarizationVersion',
    iresource=IPolarizationVersion,
    extended_sheets=(adhocracy_core.sheets.relation.IPolarization,
                     ),
    permission_create='edit_relation',
)


class IPolarization(IRelation):

    """Polarization versions pool."""


polarization_meta = item_meta._replace(
    content_name='Polarization',
    iresource=IPolarization,
    element_types=(IPolarizationVersion,
                   ),
    item_type=IPolarizationVersion,
    use_autonaming=True,
    autonaming_prefix='polarization_',
    permission_create='create_relation',
    is_implicit_addable=True
)


class IRelationsService(IServicePool):

    """The 'relations' ServicePool."""


relations_meta = service_meta._replace(
    iresource=IRelationsService,
    content_name='relations',
    element_types=(IRelation,),
)


def add_relationsservice(context: IPool,
                         registry: Registry,
                         options: dict):
    """Add `relations` service to context."""
    registry.content.create(IRelationsService.__identifier__,
                            parent=context)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(relations_meta, config)
    add_resource_type_to_registry(polarizationversion_meta, config)
    add_resource_type_to_registry(polarization_meta, config)
