# -*- coding: utf-8 -*-

import unittest

from pyramid import testing
from adhocracy.dbgraph.embeddedgraph import EmbeddedGraph
from adhocracy.dbgraph.interfaces import IGraph, IVertex, IEdge


GRAPHDB_CONNECTION_STRING = "testdb"


class DBGGraphUtilityTests(unittest.TestCase):

    def setUp(self):
        settings = {'graphdb_connection_string': GRAPHDB_CONNECTION_STRING}
        testing.setUp(settings=settings)

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
        self.g.start_transaction()
        self.g.clear()
        self.g.stop_transaction()

    def tearDown(self):
        try:
            self.g.start_transaction()
            self.g.clear()
            self.g.stop_transaction()
        finally:
            self.g.shutdown()

    # asserts the two iterables a and b contain the same set of elements.
    def assertSetEquality(self, a, b):
        def to_set(x):
            return "%s :: %s" % (list(x), type(x))
        msg = "%s and %s don't represent equal sets." % \
                (to_set(a), to_set(b))
        for i in a:
            self.assertTrue(i in b, msg)
        for i in b:
            self.assertTrue(i in a, msg)

    def assertInterface(self, interface, object):
        assert interface.providedBy(object)
        from zope.interface.verify import verifyObject
        assert verifyObject(interface, object)

    def testGetVertex(self):
        self.g.start_transaction()
        v_id = self.g.add_vertex().get_dbId()
        self.assertInterface(IVertex, self.g.get_vertex(v_id))
        self.assertEqual(v_id,
                self.g.get_vertex(v_id).get_dbId())
        self.g.stop_transaction()

    def testAddVertex(self):
        self.g.start_transaction()
        v = self.g.add_vertex()
        self.assertInterface(IVertex, v)
        assert v in self.g.get_vertices()
        self.g.stop_transaction()

    def testGetVertices(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        c = self.g.add_vertex()
        for v in self.g.get_vertices():
            self.assertInterface(IVertex, v)
        self.assertSetEquality([a, b, c], self.g.get_vertices())
        self.g.stop_transaction()

    def testRemoveVertex(self):
        self.g.start_transaction()
        v = self.g.add_vertex()
        self.g.remove_vertex(v)
        self.assertFalse(v in self.g.get_vertices())
        self.g.stop_transaction()

    def testGetEdge(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo")
        assert e.start_vertex() == a
        assert e.end_vertex() == b
        assert e.get_label() == "foo"
        self.assertInterface(IEdge, e)
        e_id = e.get_dbId()
        self.assertInterface(IEdge, self.g.get_edge(e_id))
        self.assertEqual(e_id, self.g.get_edge(e_id).get_dbId())
        self.g.stop_transaction()

    def testRemoveEdge(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo")
        self.g.remove_edge(e)
        self.assertFalse(e in self.g.get_edges())
        self.g.stop_transaction()

    def testGetEdges(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        c = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo")
        f = self.g.add_edge(b, c, "foo")
        for i in self.g.get_edges():
            self.assertInterface(IEdge, i)
        self.assertSetEquality([e, f], self.g.get_edges())
        self.g.stop_transaction()

    def testClear(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        self.g.add_edge(a, b, "connects")
        self.g.clear()
        self.assertSetEquality([], self.g.get_vertices())
        self.assertSetEquality([], self.g.get_edges())
        self.g.stop_transaction()

    #TODO: Transaction tests

if __name__ == "__main__":
    unittest.main()
