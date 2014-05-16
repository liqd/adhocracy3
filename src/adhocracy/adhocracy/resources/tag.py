"""Tag resource type."""
from adhocracy.interfaces import ITag
from adhocracy.resources import add_resource_type_to_registry


class IBasicTag(ITag):

    """Basic Tag."""


def includeme(config):
    """Register resource type factory in substanced content registry."""
    add_resource_type_to_registry(IBasicTag, config)
