"""Pool resource type."""
from adhocracy.interfaces import IPool
from adhocracy.resources import add_resource_type_to_registry


class IBasicPool(IPool):

    """Basic Pool."""


def includeme(config):
    """Register resource type factory in substanced content registry."""
    add_resource_type_to_registry(IBasicPool, config)
