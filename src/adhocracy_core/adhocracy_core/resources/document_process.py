"""Process resource which contain documents."""

from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.document import IDocument
from adhocracy_core.resources.process import IProcess
from adhocracy_core.resources.process import process_meta


class IDocumentProcess(IProcess):

    """Document participation process."""


document_process_meta = process_meta._replace(
    iresource=IDocumentProcess,
    element_types=(IDocument,
                   ),
    is_implicit_addable=True,
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(document_process_meta, config)
