"""Basic simple type without children and non versionable."""
from adhocracy_core.interfaces import ISimple
import adhocracy_core.sheets.name
import adhocracy_core.sheets.metadata
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import resource_meta
from adhocracy_core.resources.base import Base


simple_meta = resource_meta._replace(
    iresource=ISimple,
    content_class=Base,
    permission_create='create_simple',
    is_implicit_addable=False,
    basic_sheets=[adhocracy_core.sheets.name.IName,
                  adhocracy_core.sheets.title.ITitle,
                  adhocracy_core.sheets.metadata.IMetadata,
                  ],
    extended_sheets=[],
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(simple_meta, config)
