"""Logbook resource type."""
from pyramid.registry import Registry

from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.service import IServicePool
from adhocracy_core.resources.service import service_meta
from adhocracy_core.resources.document import IDocument


class ILogbookService(IServicePool):

    """The 'logbook' ServicePool."""


logbook_service_meta = service_meta._replace(
    iresource=ILogbookService,
    content_name='logbook',
    element_types=(IDocument,),
)


def add_logbook_service(context: IPool, registry: Registry, options: dict):
    """Add `logbook` service to context."""
    creator = options.get('creator')
    registry.content.create(ILogbookService.__identifier__,
                            parent=context,
                            creator=creator)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(logbook_service_meta, config)
