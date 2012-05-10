# -*- coding: utf-8 -*-

import unittest

from pyramid import testing
from adhocracy.dbgraph.embeddedgraph import EmbeddedGraph
from adhocracy.dbgraph.interfaces import IGraph


GRAPHDB_CONNECTION_STRING = "testdb"

class DBGGraphUtilityTests(unittest.TestCase):

    def setUp(self):
        settings = {'graphdb_connection_string' : GRAPHDB_CONNECTION_STRING}
        testing.setUp(settings = settings)

    def tearDown(self):
        from adhocracy.dbgraph.embeddedgraph import get_graph
        get_graph().shutdown()
        testing.tearDown()

    def test_get_graph_database_connection(self):
        from adhocracy.dbgraph.embeddedgraph import get_graph
        graph1 = get_graph()
        self.assert_(IGraph.providedBy(graph1))
        from zope.interface.verify import verifyObject
        self.assert_(verifyObject(IGraph, graph1))
        graph2 = get_graph()
        self.assert_(graph1 is graph2)


class DBGraphTestSuite(unittest.TestCase):

    def setUp(self):
        from neo4j import GraphDatabase
        db = GraphDatabase(GRAPHDB_CONNECTION_STRING)
        self.g = EmbeddedGraph(db)
        self.g.clear()

    def tearDown(self):
        self.g.clear()
        self.g.shutdown()

    def testVertices(self):
        self.g.start_transaction()
        v_id = self.g.add_vertex().get_dbId()
        self.assertEqual(v_id,
                self.g.get_vertex(v_id).get_dbId())
        self.g.stop_transaction()

if __name__ == "__main__":
    unittest.main()
