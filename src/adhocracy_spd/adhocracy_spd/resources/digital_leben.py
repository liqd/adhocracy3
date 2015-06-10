from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import document_process


class IProcess(document_process.IDocumentProcess):

    """Digital leben participation process."""


process_meta = document_process.document_process_meta._replace(
    iresource=IProcess,
    extended_sheets=[
    ],
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
