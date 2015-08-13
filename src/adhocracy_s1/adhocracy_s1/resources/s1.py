"""Resource types for s1 process."""
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process


class IProcess(process.IProcess):

    """S1 participation process."""


process_meta = process.process_meta._replace(
    iresource=IProcess,
    workflow_name='s1',
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
