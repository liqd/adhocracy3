"""Pool Sheet."""
from adhocracy.interfaces import (
    ISheet,
    IISheet,
    IResourcePropertySheet,
)
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.schema import ReferenceSetSchemaNode
from pyramid.httpexceptions import HTTPNotImplemented
from zope.interface import (
    provider,
    taggedValue,
    Interface,
    implementer,
)
from zope.interface.interfaces import IInterface

import colander


@provider(IISheet)
class IPool(ISheet):

    """Get listing with child objects of this resource."""

    taggedValue('schema', 'adhocracy.sheets.pool.PoolSchema')
    taggedValue('readonly', True)


class PoolSchema(colander.Schema):

    """Colander schema for IPool."""

    elements = ReferenceSetSchemaNode(default=[],
                                      missing=colander.drop,
                                      interfaces=[Interface],
                                      readonly=True,
                                      )


@implementer(IResourcePropertySheet)
class PoolPropertySheetAdapter(ResourcePropertySheetAdapter):

    """Adapts Pool resource  to substance PropertySheet."""

    def __init__(self, context, iface):
        assert iface.isOrExtends(IPool)
        super(PoolPropertySheetAdapter, self).__init__(context, iface)

    def get(self):
        """Return data struct."""
        struct = super(PoolPropertySheetAdapter, self).get()
        struct['elements'] = self._objectmap.pathlookup(self.context,
                                                        depth=1,
                                                        include_origin=False)
        return struct

    def set(self, struct, omit=()):
        """Return None."""
        raise HTTPNotImplemented()

    def set_cstruct(self, cstruct):
        """Return None."""
        raise HTTPNotImplemented()


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(PoolPropertySheetAdapter,
                                    (IPool, IInterface),
                                    IResourcePropertySheet)
