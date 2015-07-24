"""Resource types for s1 process."""
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
import adhocracy_s1.sheets.s1


class IProcess(process.IProcess):

    """S1 participation process."""


process_meta = process.process_meta._replace(
    iresource=IProcess,
    extended_sheets=(
        adhocracy_s1.sheets.s1.IWorkflowAssignment,
    ),
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
