"""Pool Sheet."""
from pyramid.path import DottedNameResolver
from pyramid.httpexceptions import HTTPNotImplemented
from zope.interface import provider
from zope.interface import taggedValue
from zope.interface import implementer
from zope.interface.interfaces import IInterface

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.schema import ListOfUniqueReferencesSchemaNode


class IIPool(IInterface):

    """Marker interfaces to register the pool propertysheet adapter."""


@provider(IIPool)
class IPool(ISheet):

    """Get listing with child objects of this resource."""

    taggedValue('readonly', True)
    taggedValue('field:elements',
                ListOfUniqueReferencesSchemaNode(
                    reftype='adhocracy.sheets.pool.IPoolElementsReference',
                ))


class IPoolElementsReference(SheetToSheet):

    """IPool reference."""

    source_isheet = IPool
    source_isheet_field = 'elements'
    target_isheet = ISheet


@implementer(IResourcePropertySheet)
class PoolPropertySheetAdapter(ResourcePropertySheetAdapter):

    """Adapts Pool resource  to substanced PropertySheet."""

    def get(self):
        """Return data struct."""
        struct = super().get()
        elements = []
        res = DottedNameResolver()
        reftype_ = self.schema['elements'].reftype
        reftype = res.maybe_resolve(reftype_)
        isheet = reftype.getTaggedValue('target_isheet')
        for v in self.context.values():
            if isheet.providedBy(v):
                elements.append(v)
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
