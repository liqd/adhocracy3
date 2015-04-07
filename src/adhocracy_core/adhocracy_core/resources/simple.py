"""Basic simple type without children and non versionable."""
from adhocracy_core.interfaces import ISimple
import adhocracy_core.sheets.name
import adhocracy_core.sheets.metadata
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.resource import resource_metadata_defaults


    iresource=ISimple,
    content_class=Base,
    permission_add='add_simple',
    permission_view='view',
    is_implicit_addable=False,
    basic_sheets=[adhocracy_core.sheets.name.IName,
                  adhocracy_core.sheets.metadata.IMetadata,
                  ],
    extended_sheets=[],
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(simple_metadata, config)
