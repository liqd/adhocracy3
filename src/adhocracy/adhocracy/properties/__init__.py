from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.properties import interfaces
from adhocracy.properties.interfaces import IIProperty
from adhocracy.utils import (
    get_ifaces_from_module,
    get_all_taggedvalues,
    diff_dict,
)
from adhocracy.schema import ReferenceSetSchemaNode
from collections.abc import Mapping
from pyramid.compat import is_nonstr_iter
from pyramid.interfaces import IRequest
from pyramid.httpexceptions import HTTPNotImplemented
from substanced.property import PropertySheet
from substanced.util import find_objectmap
from zope.interface import (
    implementer,
    alsoProvides,
    Interface,
)
from zope.dottedname.resolve import resolve

import colander


@implementer(IResourcePropertySheet)
class ResourcePropertySheetAdapter(PropertySheet):
    """ Read interface.."""

    def __init__(self, context, request, iface):
        assert hasattr(context, "__setitem__")
        assert iface.isOrExtends(interfaces.IProperty)
        self.context = context
        self.request = request
        self.iface = iface
        taggedvalues = get_all_taggedvalues(iface)
        self.key = taggedvalues.get("key") or iface.__identifier__
        self.permission_view = taggedvalues["permission_view"]
        self.permission_edit = taggedvalues["permission_edit"]
        schema_class = resolve(taggedvalues["schema"])
        schema_obj = schema_class()
        self.schema = schema_obj.bind(context=context, request=request)
        self._objectmap = find_objectmap(self.context)
        for child in self.schema:
            assert child.default is not colander.null
            assert child.missing is colander.drop

    @property
    def _data(self):
        if self.key not in self.context:
            self.context[self.key] = dict()
        return self.context[self.key]

    @property
    def _references(self):
        refs = {}
        for child in self.schema:
            if isinstance(child, ReferenceSetSchemaNode):
                keyname = child.name
                reftype = "{iface}:{keyname}"
                refs[keyname] = reftype.format(iface=self.iface.__identifier__,
                                               keyname=keyname)
        return refs

    def get(self):
        """read interface"""
        # fet default values
        cstruct_default = self.schema.serialize()
        # default == "" is ignored FIXME: this is  ugly
        items_empty_strs = [x for x in cstruct_default.items() if x[1] == ""]
        struct = self.schema.deserialize(cstruct_default)
        struct.update(items_empty_strs)
        # merge stored values with default values
        struct_stored = self.schema.deserialize(self._data)
        struct.update(struct_stored)
        return struct

    def set(self, struct, omit=()):
        """read interface"""
        assert isinstance(struct, Mapping)
        if not is_nonstr_iter(omit):
            omit = (omit,)
        for key in omit:
            if key in struct.keys():
                del struct[key]

        old_struct = self.get()
        changed_items = diff_dict(old_struct, struct)
        self._data.update(changed_items)

        for keyname, reftype in self._references.items():
            for target_oid in changed_items.get(keyname, []):
                self._objectmap.connect(self.context, target_oid, reftype)

        return False if not changed_items else True

    def set_cstruct(self, cstruct):
        """read interface"""
        omit = [child.name for child in self.schema
                if getattr(child, "readonly", False)]
        struct = self.schema.deserialize(cstruct)
        self.set(struct, omit=omit)

    def get_cstruct(self):
        """read interface"""
        struct = self.get()
        cstruct = self.schema.serialize(struct)
        return cstruct


@implementer(IResourcePropertySheet)
class PoolPropertySheetAdapter(ResourcePropertySheetAdapter):

    def __init__(self, context, request, iface):
        assert iface.isOrExtends(interfaces.IPool)
        super(PoolPropertySheetAdapter, self).__init__(context, request, iface)

    def get(self):
        struct = super(PoolPropertySheetAdapter, self).get()
        oids = self._objectmap.pathlookup(self.context, depth=1)
        for oid in oids:
            path = "/".join(self._objectmap.path_for(oid))
            struct["elements"].append(path)
        return struct

    def set(self, struct, omit=()):
        raise HTTPNotImplemented()

    def set_cstruct(self, cstruct):
        raise HTTPNotImplemented()


def includeme(config):
    """Iterate all IProperty interfaces and register propertysheet adapters."""

    ifaces = get_ifaces_from_module(interfaces,
                                    base=interfaces.IProperty)
    for iface in ifaces:
        alsoProvides(iface, IIProperty)
        config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                        (iface, IRequest, Interface),
                                        IResourcePropertySheet)

    config.registry.registerAdapter(PoolPropertySheetAdapter,
                                    (interfaces.IPool, IRequest, IIProperty),
                                    IResourcePropertySheet)
