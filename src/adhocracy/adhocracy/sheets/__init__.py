"""Adhocarcy sheets."""
from collections.abc import Mapping

from persistent.mapping import PersistentMapping
from pyramid.compat import is_nonstr_iter
from pyramid.path import DottedNameResolver
from substanced.property import PropertySheet
from zope.interface import implementer
import colander

from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import ISheet
from adhocracy.graph import get_references_for_isheet
from adhocracy.utils import get_all_taggedvalues
from adhocracy.utils import diff_dict
from adhocracy.utils import create_schema_from_dict
from adhocracy.schema import AbstractReferenceIterableSchemaNode


@implementer(IResourcePropertySheet)
class ResourcePropertySheetAdapter(PropertySheet):

    """Read interface.."""

    isheet = ISheet

    def __init__(self, context, iface):
        assert iface.isOrExtends(self.isheet)
        assert (not (iface.queryTaggedValue('createmandatory', False)
                and iface.queryTaggedValue('readonly', False)))
        self.context = context
        self.request = None  # just to fullfill the interface
        self.iface = iface
        taggedvalues = get_all_taggedvalues(iface)
        self.key = taggedvalues.get('key') or iface.__identifier__
        self.permission_view = taggedvalues['permission_view']
        self.permission_edit = taggedvalues['permission_edit']
        self.readonly = taggedvalues['readonly']
        self.createmandatory = taggedvalues['createmandatory']
        schema_obj = create_schema_from_dict(taggedvalues)
        self.schema = schema_obj.bind(context=context)
        for child in self.schema:
            assert child.default is not colander.null
            assert child.missing is colander.drop
        self.res = DottedNameResolver()

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
            if isinstance(child, AbstractReferenceIterableSchemaNode):
                refs[child.name] = self.res.maybe_resolve(child.reftype)
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
        cstruct = self.schema.serialize(self._data)
        struct_stored = self.schema.deserialize(cstruct)
        struct.update(struct_stored)
        # add references
        references = get_references_for_isheet(self.context, self.iface)
        for key in struct.keys():
            if key in references:
                struct[key] = references[key]
        return struct

    def set(self, struct, omit=()):
        """Return: read interface."""
        # FIXME this import is temporally hack to make unit tests work
        from adhocracy.graph import set_references
        assert isinstance(struct, Mapping)
        if not is_nonstr_iter(omit):
            omit = (omit,)

        old_struct = self.get()
        (_, changed, _) = diff_dict(old_struct, struct, omit)

        for key in changed:
            value = struct[key]
            if key in self._references.keys():
                reftype = self._references[key]
                set_references(self.context, value, reftype)
            else:
                self._data[key] = value
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
