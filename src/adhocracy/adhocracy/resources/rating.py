"""Rating resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.itemversion import itemversion_metadata
from adhocracy.resources.item import item_metadata

from adhocracy.sheets.rating import IRating


class IRatingVersion(IItemVersion):

    """Rating version."""


ratingversion_meta = itemversion_metadata._replace(
    content_name='RatingVersion',
    iresource=IRatingVersion,
    extended_sheets=[IRating],
)


class IRating(IItem):

    """Rating versions pool."""


rating_meta = item_metadata._replace(
    content_name='Rating',
    iresource=IRating,
    element_types=[IRatingVersion],
    item_type=IRatingVersion,
    use_autonaming=True,
    autonaming_prefix='rating_',
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(rating_meta, config)
    add_resource_type_to_registry(ratingversion_meta, config)
