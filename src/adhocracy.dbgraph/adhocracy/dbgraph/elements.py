# -*- coding: utf-8 -*-

from zope.dottedname.resolve import resolve
from zope.interface import implements
from zope.interface import directlyProvides

from adhocracy.dbgraph.interfaces import IElement
from adhocracy.dbgraph.interfaces import IVertex
from adhocracy.dbgraph.interfaces import IEdge


def _is_deleted_element(element):
    """Tries to guess, whether an db element is already deleted."""
    #TODO: implement using TransactionData?
    r = False
    try:
        list(element.keys())
        'foo' in element.keys()
    except Exception, e:
        r = True
    return r


class EmbeddedElement(object):
    implements(IElement)
    """implementation for EmbeddedGraph"""

    def __init__(self, db_element):

        self.db_element = db_element
        main_interface = self.get_main_interface()
        if not main_interface:
            directlyProvides(self, main_interface)

    def __eq__(self, other):
        return self.get_dbId() == other.get_dbId()

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_main_interface(self):
        if 'main_interface' in self.db_element.keys():
            return resolve(self.db_element['main_interface'])
        else:
            return IVertex

    def get_dbId(self):
        return self.db_element.id

    def get_property(self, key):
        return self.db_element[key]

    def get_properties(self):
        return dict(self.db_element)

    def set_property(self, key, value):
        self.db_element[key] = value

    def set_properties(self, property_dictionary):
        for k in property_dictionary.keys():
            self.set_property(k, property_dictionary[k])

    def remove_property(self, key):
        del self.db_element[key]


class Vertex(EmbeddedElement):
    implements(IVertex)

    def out_edges(self, label=None):
        return [Edge(edge) for edge in self.db_element.relationships.outgoing
                if not _is_deleted_element(edge)]

    def in_edges(self, label=None):
        return [Edge(edge) for edge in self.db_element.relationships.incoming
                if not _is_deleted_element(edge)]


class Edge(EmbeddedElement):
    implements(IEdge)

    def start_vertex(self):
        return Vertex(self.db_element.start)

    def end_vertex(self):
        return Vertex(self.db_element.end)

    def get_label(self):
        return self.db_element.type.name()
