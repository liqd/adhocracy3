from zope.interface import (
    implementer,
    )
from pyramid.compat import is_nonstr_iter
from substanced.property import (
    PropertySheet,
    _marker,
)
from substanced.interfaces import IPropertySheet
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from adhocracy3.schema import ReferenceSupergraphBaseSchemaNode


def set_property_object(schemanode, context, name):
    """Set a required property object to store a
       colander schema node value.
    """

    if issubclass(schemanode.__class__, ReferenceSupergraphBaseSchemaNode):
        property_obj = schemanode.property_object
        setattr(context, name, property_obj)

    if schemanode.__class__ == NameSchemaNode:
        property_obj = renamer()
        setattr(context, name, property_obj)


@implementer(IPropertySheet)
class PropertySheetAdhocracyContent(PropertySheet):
    """Subtyped to set required property objects.
    """

    def set(self, struct, omit=()):
        if not is_nonstr_iter(omit):
            omit = (omit,)
        changed = False
        for child in self.schema:
            name = child.name
            if (name in struct) and not (name in omit):
                # avoid setting an attribute on the object if it's the same
                # value as the existing value to avoid database bloat
                existing_val = getattr(self.context, name, _marker)
                new_val = struct[name]
                if existing_val != new_val:
                    # check if we have to set a attribute property object first
                    if existing_val == _marker:
                        set_property_object(child, self.context, name)
                    # now set the attribute value
                    setattr(self.context, name, new_val)
                    changed = True
        return changed
