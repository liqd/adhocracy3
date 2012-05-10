# -*- coding: utf-8 -*-

from zope.dottedname.resolve import resolve
from zope.interface import implements
from zope.interface import directlyProvides

from adhocracy.dbgraph.interfaces import IElement
from adhocracy.dbgraph.interfaces import IVertex
from adhocracy.dbgraph.interfaces import IEdge


class EmbeddedElement(object):

    implements(IElement)

    def __init__(self, db_element):

        self.db_element = db_element
        main_interface = self.get_main_interface()
        if not main_interface:
            directlyProvides(self, main_interface)

    def get_main_interface(self):
        interface_name = self.db_element['main_interface']
        return resolve(interface_name) if interface_name else None

    def get_dbId(self):
        return self.db_element.id

    def get_property(key):
        """Gets the value of the property for the given key"""

    def get_properties():
        """Returns a dictionary with all properties (key/value)"""

    def set_property(key, value):
        """Sets the property of the element to the given value"""

    def set_properties(property_dictionary):
        """Add properties. Existing properties are replaced."""

    def remove_property(self, key):
        """Removes the value of the property for the given key"""


class Vertex(EmbeddedElement):

    implements(IVertex)


class Edge(EmbeddedElement):
    implements(IEdge)
