"""Adhocarcy sheets."""
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import ISheet
from adhocracy.utils import get_all_taggedvalues
from adhocracy.utils import diff_dict
from adhocracy.schema import ReferenceSetSchemaNode
from collections.abc import Mapping
from persistent.mapping import PersistentMapping
from pyramid.compat import is_nonstr_iter
from pyramid.path import DottedNameResolver
from substanced.property import PropertySheet
from substanced.util import find_objectmap
from zope.interface import implementer

import colander


@implementer(IResourcePropertySheet)
class ResourcePropertySheetAdapter(PropertySheet):

    """Read interface.."""

    isheet = ISheet

    def __init__(self, context, iface):
        assert hasattr(context, '__setitem__')
        assert iface.isOrExtends(self.isheet)
        assert (not (iface.queryTaggedValue('createmandatory', False)
                and iface.queryTaggedValue('readonly', False)))
        res = DottedNameResolver()
        self.context = context
        self.request = None  # just to fullfill the interface
        self.iface = iface
        taggedvalues = get_all_taggedvalues(iface)
        self.key = taggedvalues.get('key') or iface.__identifier__
        self.permission_view = taggedvalues['permission_view']
        self.permission_edit = taggedvalues['permission_edit']
        self.readonly = taggedvalues['readonly']
        self.createmandatory = taggedvalues['createmandatory']
        schema_class = res.maybe_resolve(taggedvalues['schema'])
        schema_obj = schema_class()
        self.schema = schema_obj.bind(context=context)
        self._objectmap = find_objectmap(self.context)
        for child in self.schema:
            assert child.default is not colander.null
            assert child.missing is colander.drop

    @property
    def _data(self):
        if not hasattr(self.context, '_propertysheets'):
            self.context._propertysheets = PersistentMapping()
        if self.key not in self.context._propertysheets:
            self.context._propertysheets[self.key] = PersistentMapping()
        return self.context._propertysheets[self.key]

    @property
    def _references(self):
        refs = {}
        for child in self.schema:
            if isinstance(child, ReferenceSetSchemaNode):
                keyname = child.name
                reftype = '{iface}:{keyname}'
                refs[keyname] = reftype.format(iface=self.iface.__identifier__,
                                               keyname=keyname)
        return refs

    def get(self):
        """Return: read interface."""
        # fet default values
        cstruct_default = self.schema.serialize()
        # default == '' is ignored FIXME: this is  ugly
        items_empty_strs = [x for x in cstruct_default.items() if x[1] == '']
        struct = self.schema.deserialize(cstruct_default)
        struct.update(items_empty_strs)
        # merge stored values with default values
        struct_stored = self.schema.deserialize(self._data)
        struct.update(struct_stored)
        return struct

    def set(self, struct, omit=()):
        """Return: read interface."""
        assert isinstance(struct, Mapping)
        if not is_nonstr_iter(omit):
            omit = (omit,)

        old_struct = self.get()
        (_, changed, _) = diff_dict(old_struct, struct, omit)

        for key in changed:
            self._data[key] = struct[key]

            if key in self._references.keys():
                reftype = self._references[key]
                for oid in set(struct[key]) - set(old_struct[key]):
                    self._objectmap.connect(self.context, oid, reftype)
                for oid in set(old_struct[key]) - set(struct[key]):
                    self._objectmap.disconnect(self.context, oid, reftype)

        return bool(changed)

    def validate_cstruct(self, cstruct):
        """Return: read interface."""
        for child in self.schema:
            if getattr(child, 'readonly', False):
                raise colander.Invalid(child, msg=u'This key is readonly')
        struct = self.schema.deserialize(cstruct)
        return struct

    def get_cstruct(self):
        """Return: read interface."""
        struct = self.get()
        cstruct = self.schema.serialize(struct)
        return cstruct


def includeme(config):
    """Include all sheets in this package."""
    config.include('.name')
    config.include('.pool')
    config.include('.document')
    config.include('.versions')
    config.include('.tags')
