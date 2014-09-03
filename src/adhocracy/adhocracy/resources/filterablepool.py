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

    def filtered_elements(self, *filters) -> Iterable:
        """Return elements accepted by all specified filters."""
        catalog = find_catalog(self, 'system')
        path = catalog['path']
        # find all direct children of inst
        q = path.eq(resource_path(self), depth=1, include_origin=False)
        resultset = q.execute()
        for result in resultset:
            yield result

    def interface_filter(self, iface) -> Iterable:
        # TODO testing only
        catalog = find_catalog(self, 'system')
        path = catalog['path']
        assert len(path.docids()) == 1  # TODO why is this??
        name = catalog['name']
        assert len(name.docids()) == 1
        interfaces = catalog['interfaces']
        assert len(interfaces.docids()) == 1
        q = interfaces.eq(iface)
        resultset = q.execute()
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
