# -*- coding: utf-8 -*-

import unittest
from zope.interface import Interface

from adhocracy.dbgraph.interfaces import IVertex
from adhocracy.dbgraph.interfaces import IEdge
from adhocracy.dbgraph.interfaces import INode
from adhocracy.dbgraph.interfaces import ILocationAware
from adhocracy.dbgraph.interfaces import IReference
from adhocracy.dbgraph.interfaces import DontRemoveRootException
from adhocracy.dbgraph.embeddedgraph import EmbeddedGraph
from adhocracy.dbgraph.embeddedgraph import get_graph
from adhocracy.dbgraph.embeddedgraph import del_graph


GRAPHDB_CONNECTION_STRING = "testdb"


class IDummyMarker(Interface):
    """buh"""


class IDummyNodeMarker(INode):
    """bah"""


class IDummyReferenceMarker(IReference):
    """bih"""


def assertSetEquality(a, b):
    """asserts the two iterables a and b contain the same set of elements"""
    def to_set(x):
        return "%s :: %s" % (list(x), type(x))
    msg = "%s and %s don't represent equal sets." % \
            (to_set(a), to_set(b))
    for i in a:
        assert i in b, msg
    for i in b:
        assert i in a, msg


def assertInterface(interface, obj):
    assert interface.providedBy(obj)
    from zope.interface.verify import verifyObject
    assert verifyObject(interface, obj)


class DBGraphTest(unittest.TestCase):

    @classmethod
    def setup_class(self):
        from neo4j import GraphDatabase
        db = GraphDatabase(GRAPHDB_CONNECTION_STRING)
        self.g = EmbeddedGraph(db)

    @classmethod
    def teardown_class(self):
        self.g.shutdown()
        del self.g

    def tearDown(self):
        try:
            #catch aborted transactions
            self.g.stop_transaction()
        except Exception:
            pass
        self.g.start_transaction()
        self.g.clear()
        self.g.stop_transaction()

    def testGetVertex(self):
        self.g.start_transaction()
        v_id = self.g.add_vertex().get_dbId()
        assertInterface(IVertex, self.g.get_vertex(v_id))
        self.assertEqual(v_id,
                self.g.get_vertex(v_id).get_dbId())
        self.g.stop_transaction()

    def testAddVertex(self):
        self.g.start_transaction()
        v = self.g.add_vertex()
        assertInterface(IVertex, v)
        assert v in self.g.get_vertices()
        self.g.stop_transaction()

    def testAddVertexWithMarkerInterface(self):
        self.g.start_transaction()
        v = self.g.add_vertex(main_interface=IDummyMarker)
        assertInterface(IVertex, v)
        assertInterface(IDummyMarker, v)
        self.g.stop_transaction()

    def testAddNode(self):
        self.g.start_transaction()
        v = self.g.add_vertex(main_interface=IDummyNodeMarker)
        assertInterface(IVertex, v)
        assertInterface(INode, v)
        assertInterface(IDummyNodeMarker, v)
        assertInterface(ILocationAware, v)
        assert v in self.g.get_vertices()
        self.g.stop_transaction()

    def testGetVertices(self):
        self.g.start_transaction()
        root = self.g.get_root_vertex()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        c = self.g.add_vertex()
        for v in self.g.get_vertices():
            assertInterface(IVertex, v)
        assertSetEquality([root, a, b, c], self.g.get_vertices())
        self.g.stop_transaction()

    def testRemoveVertex(self):
        self.g.start_transaction()
        v = self.g.add_vertex()
        self.g.remove_vertex(v)
        self.assertFalse(v in self.g.get_vertices())
        self.g.stop_transaction()

    def testAddEdge(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo")
        self.g.stop_transaction()
        assert e.start_vertex() == a
        assert e.end_vertex() == b
        assert e.get_label() == "foo"
        assertInterface(IEdge, e)
        e_id = e.get_dbId()
        assertInterface(IEdge, self.g.get_edge(e_id))
        self.assertEqual(e_id, self.g.get_edge(e_id).get_dbId())

    def testAddEdgeWithMarkerInterface(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo", main_interface=IDummyMarker)
        self.g.stop_transaction()
        assertInterface(IEdge, e)
        assertInterface(IDummyMarker, e)

    def testAddReference(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo", main_interface=IDummyReferenceMarker)
        self.g.stop_transaction()
        assertInterface(IEdge, e)
        assertInterface(IReference, e)
        assertInterface(IDummyReferenceMarker, e)

    def testGetEdge(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo")
        e_id = e.get_dbId()
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
            assertInterface(IEdge, i)
        assertSetEquality([e, f], self.g.get_edges())
        self.g.stop_transaction()

    def testClear(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        self.g.add_edge(a, b, "connects")
        self.g.clear()
        root = self.g.get_root_vertex()
        assertSetEquality([root], self.g.get_vertices())
        assertSetEquality([], root.get_properties().keys())
        assertSetEquality([], self.g.get_edges())
        self.g.stop_transaction()

    def testGetRootVertex(self):
        root = self.g.get_root_vertex()
        assertInterface(IVertex, root)
        assertSetEquality([self.g.get_root_vertex()], self.g.get_vertices())

    def testRemvoeRootVertex(self):
        import pytest
        with pytest.raises(DontRemoveRootException):
            self.g.start_transaction()
            root = self.g.get_root_vertex()
            self.g.remove_vertex(root)
            self.g.stop_transaction()

    def testGetProperties(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "connects")
        ap = {'foo': 42, 'bar': 23}
        a.set_properties(ap)
        ep = {'baz': 42, 'blub': 23}
        e.set_properties(ep)
        assert ap == a.get_properties()
        assert ep == e.get_properties()
        self.g.stop_transaction()

    def testGetProperty(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "connects")
        ap = {'foo': 42, 'bar': 23}
        a.set_properties(ap)
        ep = {'baz': 42, 'blub': 23}
        e.set_properties(ep)
        for k in ap.keys():
            assert ap[k] == a.get_property(k)
        for k in ep.keys():
            assert ep[k] == e.get_property(k)
        self.g.stop_transaction()

    def testRemoveProperty(self):
        self.g.start_transaction()
        v = self.g.get_root_vertex()
        v.set_property("key", "value")
        assert (v.get_property("key") == "value")
        v.remove_property("key")
        assert "key" not in v.get_properties().keys()
        self.g.stop_transaction()

    def testInOutEdges(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        c = self.g.add_vertex()
        A = self.g.add_edge(a, b, "A")
        B = self.g.add_edge(b, c, "B")
        C = self.g.add_edge(c, a, "C")
        assertSetEquality([A], a.out_edges())
        assertSetEquality([C], a.in_edges())
        assertSetEquality([B], b.out_edges())
        assertSetEquality([A], b.in_edges())
        assertSetEquality([C], c.out_edges())
        assertSetEquality([B], c.in_edges())
        self.g.stop_transaction()


#@Sönke Why do want to run all tests twice?
#class GetGraphEmbeddedTestSuite(DBGraphTestSuite):
    #"""Like DBGraphTestSuite, but the graph is created using get_graph."""

    #@classmethod
    #def setup_class(self):
        #from pyramid import testing
        #settings = {'graphdb_connection_string': GRAPHDB_CONNECTION_STRING}
        #config = testing.setUp(settings=settings)
        #self.g = get_graph()
        #self.g.start_transaction()
        #self.g.clear()
        #self.g.stop_transaction()

    #def tearDown(self):
        #self.g.start_transaction()
        #self.g.clear()
        #self.g.stop_transaction()
        #del_graph()
        #from pyramid import testing
        #testing.tearDown()

    ##TODO: Transaction tests


if __name__ == "__main__":
    unittest.main()
