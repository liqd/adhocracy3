"""'Simple page resource type."""
from pyramid.registry import Registry

from adhocracy_core.interfaces import ISimple
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.simple import simple_meta
from adhocracy_core.resources.service import service_meta

import adhocracy_core.sheets


class IPage(ISimple):
    """A simple page."""


page_meta = simple_meta._replace(
    content_name='Page',
    iresource=IPage,
    use_autonaming=False,
    basic_sheets=(adhocracy_core.sheets.name.IName,
                  adhocracy_core.sheets.title.ITitle,
                  adhocracy_core.sheets.description.IDescription,
                  adhocracy_core.sheets.metadata.IMetadata,
                  ),
    permission_create='create_page',
    is_sdi_addable=True,

)


class IPageService(IServicePool):
    """The 'page' ServicePool."""


page_service_meta = service_meta._replace(
    iresource=IPageService,
    content_name='pages',
    element_types=(IPage,),
)


def add_page_service(context: IPool, registry: Registry, options: dict):
    """Add `page` service to context."""
    registry.content.create(IPageService.__identifier__,
                            parent=context,
                            autoupdated=True)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(page_meta, config)
    add_resource_type_to_registry(page_service_meta, config)
