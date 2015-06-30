"""TAG type to label itemversions."""
from adhocracy_core.interfaces import ITag
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import resource_meta
from adhocracy_core.resources.base import Base
import adhocracy_core.sheets.name
import adhocracy_core.sheets.tags
import adhocracy_core.sheets.metadata


tag_meta = resource_meta._replace(
    iresource=ITag,
    content_class=Base,
    permission_create='create_tag',
    permission_edit='edit',
    is_implicit_addable=False,
    basic_sheets=[adhocracy_core.sheets.name.IName,
                  adhocracy_core.sheets.metadata.IMetadata,
                  adhocracy_core.sheets.tags.ITag,
                  ],
    extended_sheets=[],
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(tag_meta, config)
