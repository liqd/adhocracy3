# -*- coding: utf-8 -*-

from neo4j import GraphDatabase

from zope.interface import implements

from adhocracy.dbgraph.interfaces import IGraph


class EmbeddedGraph():
    implements(IGraph)

    def __init__(self, connection_string):
        """Creates a new GraphConnection"""

        self.db = GraphDatabase(connection_string)

    def shutdown(self):
        """Closes graph connection"""

        self.db.shutdown()

    def __init__(connection_string):
        """Creates a new GraphConnection"""

    def add_vertex(main_interface=IVertex):
        """Adds a new vertex to the graph with the given
           Interface.
        """

    def get_vertex(dbid):
        """Retrieves an existing vertex from the graph
           with the given dbid or None.
        """

    def get_vertices():
        """Returns an iterator with all the vertices"""

    def remove_vertex(vertex):
        """Removes the given vertex"""

    def add_edge(self, startVertex, endVertex, label, main_interface=IEdge):
        """Creates a new edge with label(String)"""

    def get_edge(dbid):
        """Retrieves an existing edge from the graph
           with the given dbid or None.
        """

    def get_edges():
        """Returns an iterator with all the vertices"""

    def remove_edge(edge):
        """Removes the given edge"""

    def clear():
        """Dooms day machine"""

    def start_transaction():
        """Start Transaction to add new or create Elements"""

    def stop_transaction():
        """Stop Transaction"""
