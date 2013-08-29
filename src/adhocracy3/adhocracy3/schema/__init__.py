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
    return map(lambda x: (get_oid(x), x.name), docs)


class ReferenceSupergraphBaseSchemaNode(schema.MultireferenceIdSchemaNode):

   default=[]
   missing=[]
   choices_getter = get_all_content

   interface = Interface
   # attribute property class to store reference values
   property_class = reference_sourceid_property

   @property
   def reference_type(self):
       return self.name


class ReferenceSetSchemaNode(ReferenceSupergraphBaseSchemaNode):
    pass
