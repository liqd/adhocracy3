"""Basic participation process."""
from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import pool_meta


class IProcess(IPool):

    """Participation Process Pool."""


process_meta = pool_meta._replace(
    iresource=IProcess,
    # Every process should have a workflow assignment sheet, for example
    # extended_sheets=[adhocracy_core.sheets.workflow.sample]
    permission_add='add_process',
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(process_meta, config)
