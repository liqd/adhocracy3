"""Alexanderplatz process resources."""

from adhocracy_core.resources.document_process import document_process_meta
from adhocracy_core.resources.document_process import IDocumentProcess
from adhocracy_core.resources import add_resource_type_to_registry


class IProcess(IDocumentProcess):

    """Alexanderplatz participation process."""


process_meta = document_process_meta._replace(
    iresource=IProcess
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
