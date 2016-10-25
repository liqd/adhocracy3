"""Resource types for collaborative text process."""
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import document_process
from adhocracy_core.sheets.image import IImageReference


class IProcess(document_process.IDocumentProcess):
    """Collaborative text participation process."""


process_meta = document_process.document_process_meta._replace(
    content_name='CollaborativeTextProcess',
    iresource=IProcess,
    default_workflow='debate',
    extended_sheets=(
        IImageReference,
    ),
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
