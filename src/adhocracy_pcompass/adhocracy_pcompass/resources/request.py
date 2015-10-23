"""Policy compass process resources."""

from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources.proposal import IProposal


class IProcess(process.IProcess):
    """Policy Compass participation process."""

process_meta = process.process_meta._replace(
    iresource=IProcess,
    element_types=(IProposal,),
    workflow_name='standard',
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
