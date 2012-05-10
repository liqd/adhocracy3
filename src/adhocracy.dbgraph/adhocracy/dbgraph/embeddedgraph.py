# -*- coding: utf-8 -*-
import atexit
from zope.interface import implements
from zope.interface import implementer
from zope import component
from pyramid.threadlocal import get_current_registry

from adhocracy.dbgraph.interfaces import IGraph
from adhocracy.dbgraph.interfaces import IVertex
from adhocracy.dbgraph.interfaces import IEdge

from adhocracy.dbgraph.elements import Vertex


class EmbeddedGraph():
    implements(IGraph)

    def __init__(self, dbgraph_database):
        self.db = dbgraph_database

    def shutdown(self):
        self.db.shutdown()

    def add_vertex(self, main_interface=IVertex):
        """
        >>> import adhocracy.dbgraph.tests
        >>> adhocracy.dbgraph.tests.setUp()
        <py...
        >>> g = get_graph()
        >>> g.start_transaction()
        >>> v = g.add_vertex()
        >>> print(v in g.get_vertices())
        True
        >>> g.start_transaction()
        >>> g.shutdown()
        >>> adhocracy.dbgraph.tests.tearDown()
        """
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


def get_graph():
    """ returns the graph database connection object
    """
    global_registry = component.getGlobalSiteManager()
    graph = global_registry.queryUtility(IGraph)
    if not graph:
        global_registry = component.getGlobalSiteManager()
        graph = graph_factory()
        global_registry.registerUtility(graph, IGraph)
    return graph


implementer(IGraph)
def graph_factory():
    """Utility to store the db graph conneciton object
    """
    settings = get_current_registry().settings
    connection_string = settings['graphdb_connection_string'] or "testdb"
    import os
    os.environ['NEO4J_PYTHON_JVMARGS'] = '-Xms128M -Xmx512M'
    from neo4j import GraphDatabase
    db = GraphDatabase(connection_string)
    return EmbeddedGraph(db)


def _close_db():
    """Make sure to always close the database
    """
    try:
        graph = get_graph()
        graph.shutdown()
    except NameError:
        print 'Could not shutdown Neo4j database.'

atexit.register(_close_db)
