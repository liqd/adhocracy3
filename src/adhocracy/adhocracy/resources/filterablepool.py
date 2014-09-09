"""Pools that can be filtered."""
from collections.abc import Iterable

from pyramid.traversal import resource_path
from substanced.interfaces import IFolder
from substanced.util import find_catalog
from zope.interface import implementer

from adhocracy.interfaces import IFilterablePool
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.pool import Pool
from adhocracy.resources.pool import pool_metadata


class IBasicFilterablePool(IFilterablePool):

    """Basic filterable pool."""


@implementer(IFilterablePool, IFolder)
class FilterablePool(Pool):

    """A pool that can be filtered and aggregated."""

    def filtered_elements(self, depth=1, ifaces: Iterable=None) -> Iterable:
        """See interface for docstring."""
        system_catalog = find_catalog(self, 'system')
        path_index = system_catalog['path']
        query = path_index.eq(resource_path(self), depth=depth,
                              include_origin=False)
        if ifaces:
            interface_index = system_catalog['interfaces']
            query &= interface_index.all(ifaces)
        resultset = query.execute()
        for result in resultset:
            yield result


filterable_pool_metadata = pool_metadata._replace(
    content_name=IBasicFilterablePool.__identifier__,
    iresource=IBasicFilterablePool,
    content_class=FilterablePool,
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(filterable_pool_metadata, config)
