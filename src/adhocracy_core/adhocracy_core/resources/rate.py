"""Rate resource type."""
from pyramid.registry import Registry

from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_meta
from adhocracy_core.resources.item import item_meta
from adhocracy_core.resources.service import service_meta

from adhocracy_core.sheets.rate import IRate


class IRateVersion(IItemVersion):

    """Rate version."""


rateversion_meta = itemversion_meta._replace(
    iresource=IRateVersion,
    extended_sheets=[IRate],
    permission_create='edit_rate',
)


class IRate(IItem):

    """Rate versions pool."""


rate_meta = item_meta._replace(
    iresource=IRate,
    element_types=[IRateVersion],
    item_type=IRateVersion,
    use_autonaming=True,
    autonaming_prefix='rate_',
    permission_create='create_rate',
)


class IRatesService(IServicePool):

    """The 'rates' ServicePool."""


rates_meta = service_meta._replace(
    iresource=IRatesService,
    content_name='rates',
    element_types=[IRate],
)


def add_ratesservice(context: IPool, registry: Registry, options: dict):
    """Add `rates` service to context."""
    registry.content.create(IRatesService.__identifier__, parent=context)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(rate_meta, config)
    add_resource_type_to_registry(rateversion_meta, config)
    add_resource_type_to_registry(rates_meta, config)
