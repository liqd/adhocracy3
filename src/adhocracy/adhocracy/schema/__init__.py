from zope.interface import (
    Interface,
    )
from pyramid.threadlocal import get_current_request
from substanced import schema
from substanced.util import (
    find_catalog,
    get_oid,
    )
from substanced.objectmap import reference_sourceid_property
from substanced.util import find_objectmap
import colander


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

   def serialize(self, appstruct = colander.null):
        oids = list(colander.SchemaNode.serialize(self, appstruct))
        request = get_current_request()
        object_map = find_objectmap(request.context)

        refs = []
        for string_oid in oids:
            path = "/".join(object_map.path_for(int(string_oid)))
            refs.append(path)
        return refs



class ReferenceSetSchemaNode(ReferenceSupergraphBaseSchemaNode):
    pass
