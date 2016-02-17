"""Idea collection process."""

from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources.proposal import IProposal


class IProcess(process.IProcess):
    """Idea collection participation process."""

process_meta = process.process_meta._replace(
    iresource=IProcess,
    element_types=(IProposal,),
    workflow_name='standard',
)


class IPrivateProcess(process.IProcess):
    """Private idea collection participation process."""


private_process_meta = process.process_meta._replace(
    iresource=IPrivateProcess,
    element_types=(IProposal,),
    workflow_name='standard_private',
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
    add_resource_type_to_registry(private_process_meta, config)
