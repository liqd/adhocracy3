"""Autoupdate the workflow state of resources."""
from pyramid.registry import Registry
from substanced.workflow import IWorkflow
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.utils import get_isheets


def initialize_workflows(event):
    """Initialize workflows for `event.object`."""
    workflows = _get_workflows(event.object, event.registry)
    for workflow in workflows:
        if workflow.has_state(event.object):
            continue
        workflow.initialize(event.object)


def _get_workflows(context, registry: Registry) -> [IWorkflow]:
    isheets = [i for i in get_isheets(context)
               if i.isOrExtends(IWorkflowAssignment)]
    for isheet in isheets:
        workflow = get_sheet_field(context, isheet, 'workflow', registry)
        yield workflow


def includeme(config):
    """Add subscriber."""
    config.add_subscriber(initialize_workflows,
                          IResourceCreatedAndAdded,
                          object_iface=IWorkflowAssignment)
