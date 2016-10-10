"""Basic organisation pool to structure processes."""
from pyramid.registry import Registry

from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.asset import add_assets_service
from adhocracy_core.resources.pool import pool_meta
from adhocracy_core.resources.process import IProcess
from adhocracy_core.sheets.asset import IHasAssetPool
from adhocracy_core.sheets.description import IDescription
from adhocracy_core.sheets.image import IImageReference
from adhocracy_core.sheets.notification import IFollowable
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.utils import get_iresource


class IOrganisation(IPool):
    """Organisation Pool."""


def enabled_ordering(pool: IPool, registry: Registry, **kwargs):
    """Enabled ordering for `pool` children."""
    initial_order = list(pool.keys())
    if hasattr(pool, '__oid__'):  # ease testing
        pool.set_order(initial_order, reorderable=True)


def sdi_organisation_columns(folder, subobject, request, default_columnspec):
    """Mapping function to add info columns to the sdi organisation listing."""
    content = request.registry.content
    content_name = ''
    title = ''
    if subobject:
        iresource = get_iresource(subobject)
        metadata = content.resources_meta[iresource]
        content_name = metadata.content_name
        if IProcess.providedBy(subobject):
            title = content.get_sheet_field(subobject, ITitle, 'title')
    additional_columns = [
        {'name': 'Type', 'value': content_name},
        {'name': 'Title', 'value': title},
    ]
    return default_columnspec + additional_columns


organisation_meta = pool_meta._replace(
    content_name='Organisation',
    iresource=IOrganisation,
    permission_create='create_organisation',
    is_implicit_addable=True,
    is_sdi_addable=True,
    sdi_column_mapper=sdi_organisation_columns,
    element_types=(IProcess,
                   IOrganisation,
                   ),
    after_creation=(add_assets_service,
                    enabled_ordering)
)._add(basic_sheets=(IDescription,
                     IImageReference,
                     IFollowable,
                     ),
       extended_sheets=(IHasAssetPool,),)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(organisation_meta, config)
