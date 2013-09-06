from zope.interface import (
    Interface,
    )
from substanced import schema
from substanced.util import (
    find_catalog,
    get_oid,
    )
from substanced.objectmap import reference_sourceid_property


def get_all_content(node, context, request):
    interface = node.interface
    catalog = find_catalog(context, 'system')
    interfaces = catalog['interfaces']
    docs = interfaces.eq(interface).execute().all()
    return map(lambda x: (get_oid(x), getattr(x, "name", None) or
                          x.__name__),
               [d for d in docs if d])


class ReferenceSupergraphBaseSchemaNode(schema.MultireferenceIdSchemaNode):

   default=[]
   missing=[]
   choices_getter = get_all_content

   interface = Interface

   @property
   def property_object(self):
       """Property object to store reference values"""

       reference_type = self.name
       return reference_sourceid_property(reference_type)


class ReferenceSetSchemaNode(ReferenceSupergraphBaseSchemaNode):
    pass
