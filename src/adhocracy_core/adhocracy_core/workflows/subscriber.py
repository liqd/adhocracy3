"""Autoupdate the workflow state of resources."""
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IResourceCreatedAndAdded


def initialize_workflow(event):
    """Initialize workflow for `event.object`."""
    workflow = event.registry.content.get_workflow(event.object)
    if workflow is None:
        return
    if workflow.has_state(event.object):
        return
    workflow.initialize(event.object)


def includeme(config):
    """Add subscriber."""
    config.add_subscriber(initialize_workflow,
                          IResourceCreatedAndAdded,
                          object_iface=IResource)
