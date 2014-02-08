"""Pool Sheet."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.schema import ReferenceSetSchemaNode
from pyramid.path import DottedNameResolver
from pyramid.httpexceptions import HTTPNotImplemented
from substanced.util import get_oid
from zope.interface import provider
from zope.interface import taggedValue
from zope.interface import implementer
from zope.interface.interfaces import IInterface

import colander


class IIPool(IInterface):

    """Marker interfaces to register the pool propertysheet adapter."""


@provider(IIPool)
class IPool(ISheet):

    """Get listing with child objects of this resource."""

    taggedValue('readonly', True)
    taggedValue('field:elements',
                ReferenceSetSchemaNode(default=[],
                                       missing=colander.drop,
                                       interfaces=[IResource],
                                       )
                )


@implementer(IResourcePropertySheet)
class PoolPropertySheetAdapter(ResourcePropertySheetAdapter):

    """Adapts Pool resource  to substanced PropertySheet."""

    def get(self):
        """Return data struct."""
        struct = super(PoolPropertySheetAdapter, self).get()
        elements = []
        res = DottedNameResolver()
        elements_ifaces = self.schema['elements'].interfaces
        ifaces = [res.maybe_resolve(i) for i in elements_ifaces]
        for v in self.context.values():
            for i in ifaces:
                if i.providedBy(v):
                    elements.append(get_oid(v))
                    break
        struct['elements'] = elements
        return struct

    def set(self, struct, omit=()):
        """Return None."""
        raise HTTPNotImplemented()

    def validate_cstruct(self, cstruct):
        """Return None."""
        raise HTTPNotImplemented()


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(PoolPropertySheetAdapter,
                                    (IPool, IIPool),
                                    IResourcePropertySheet)
