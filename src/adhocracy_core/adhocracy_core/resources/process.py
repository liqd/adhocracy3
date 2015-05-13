"""Basic participation process."""
from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import pool_meta
from adhocracy_core.resources.asset import add_assets_service
from adhocracy_core import sheets


class IProcess(IPool):

    """Participation Process Pool."""


process_meta = pool_meta._replace(
    iresource=IProcess,
    basic_sheets=pool_meta.basic_sheets + [sheets.asset.IHasAssetPool],
    # Every process should have a workflow assignment sheet, for example
    # extended_sheets=[adhocracy_core.sheets.workflow.sample]
    permission_create='create_process',
    after_creation=[add_assets_service],
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(process_meta, config)
