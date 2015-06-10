"""Resource types for digital leben process."""
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import document_process
import adhocracy_spd.sheets.digital_leben


class IProcess(document_process.IDocumentProcess):

    """Digital leben participation process."""


process_meta = document_process.document_process_meta._replace(
    iresource=IProcess,
    extended_sheets=[
        adhocracy_spd.sheets.digital_leben.IWorkflowAssignment,
    ],
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
