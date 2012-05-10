# -*- coding: utf-8 -*-

from neo4j import GraphDatabase
from zope.interface import implements
from pyramid.threadlocal import get_current_registry

from adhocracy.dbgraph.interfaces import IGraph
from adhocracy.dbgraph.interfaces import IVertex
from adhocracy.dbgraph.interfaces import IEdge

from adhocracy.dbgraph.elements import Vertex


class EmbeddedGraph():
    implements(IGraph)

    def __init__(self, connection_string):
        self.db = GraphDatabase(connection_string)

    def shutdown(self):
        self.db.shutdown()

    def add_vertex(self, main_interface=IVertex):
        db_vertex = self.db.node()
        db_vertex['main_interface'] = main_interface.__identifier__
        return Vertex(db_vertex)

    def get_vertex(self, dbid):
        db_vertex = self.db.node[dbid]
        return Vertex(db_vertex)

    def get_vertices(self):
        """Returns an iterator with all the vertices"""

    def remove_vertex(self, vertex):
        """Removes the given vertex"""

    def add_edge(self, in_vertex, out_vertex, label, main_interface=IEdge):
        """Creates a new edge with label(String)"""

    def get_edge(self, dbid):
        """Retrieves an existing edge from the graph
           with the given dbid or None.
        """

    def get_edges(self):
        """Returns an iterator with all the vertices"""

    def remove_edge(self, edge):
        """Removes the given edge"""

    def clear(self):
        """Dooms day machine"""

    def start_transaction(self):
        self.transaction = self.db.beginTx()

    def stop_transaction(self):
        self.transaction.success()
        self.transaction.finish()


def graph_factory():
    registry = get_current_registry()
    connection_string = registry.settings['graphdb_connection_string']
    return EmbeddedGraph(connection_string)

