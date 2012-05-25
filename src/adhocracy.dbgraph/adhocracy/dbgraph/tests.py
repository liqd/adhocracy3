# -*- coding: utf-8 -*-

import unittest
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope import schema

from adhocracy.dbgraph.interfaces import IVertex
from adhocracy.dbgraph.interfaces import IEdge
from adhocracy.dbgraph.interfaces import INode
from adhocracy.dbgraph.interfaces import ILocationAware
from adhocracy.dbgraph.interfaces import IReference
from adhocracy.dbgraph.interfaces import DontRemoveRootException
from adhocracy.dbgraph.embeddedgraph import EmbeddedGraph
from adhocracy.dbgraph.fieldproperty import AdoptedFieldProperty

GRAPHDB_CONNECTION_STRING = "testdb"


class IDummyMarker(Interface):
    """buh"""


class IDummyNodeMarker(INode):
    """bah"""


class IDummyReferenceMarker(IReference):
    """bih"""


class IDummyNodeWithFields(INode):
    """blub"""

    first_names = schema.Tuple(
                    title=u"First names",
                    #global default value, think before you do this
                    default=(u"default name",),
                    value_type=schema.TextLine(title=u"name")
                    )


class DummyNodeWithFieldsAdapter(object):
    """blub"""

    implements(IDummyNodeWithFields)
    adapts(INode)

    def __init__(self, context):
        self.context = context

    first_names = AdoptedFieldProperty(IDummyNodeWithFields["first_names"])


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
        tx = self.g.start_transaction()
        self.g.clear()
        self.g.stop_transaction(tx)

    def testGetVertex(self):
        tx = self.g.start_transaction()
        v_id = self.g.add_vertex().get_dbId()
        assertInterface(IVertex, self.g.get_vertex(v_id))
        self.assertEqual(v_id,
                self.g.get_vertex(v_id).get_dbId())
        self.g.stop_transaction(tx)

    def testAddVertex(self):
        tx = self.g.start_transaction()
        v = self.g.add_vertex()
        assertInterface(IVertex, v)
        assert v in self.g.get_vertices()
        self.g.stop_transaction(tx)

    def testAddVertexWithMarkerInterface(self):
        tx = self.g.start_transaction()
        v = self.g.add_vertex(main_interface=IDummyMarker)
        assertInterface(IVertex, v)
        assertInterface(IDummyMarker, v)
        self.g.stop_transaction(tx)

    def testAddNode(self):
        tx = self.g.start_transaction()
        v = self.g.add_vertex(main_interface=IDummyNodeMarker)
        assertInterface(IVertex, v)
        assertInterface(INode, v)
        assertInterface(IDummyNodeMarker, v)
        assertInterface(ILocationAware, v)
        assert v in self.g.get_vertices()
        self.g.stop_transaction(tx)

    def testGetVertices(self):
        tx = self.g.start_transaction()
        root = self.g.get_root_vertex()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        c = self.g.add_vertex()
        for v in self.g.get_vertices():
            assertInterface(IVertex, v)
        assertSetEquality([root, a, b, c], self.g.get_vertices())
        self.g.stop_transaction(tx)

    def testRemoveVertex(self):
        tx = self.g.start_transaction()
        v = self.g.add_vertex()
        self.g.remove_vertex(v)
        self.assertFalse(v in self.g.get_vertices())
        self.g.stop_transaction(tx)

    def testAddEdge(self):
        tx = self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo")
        self.g.stop_transaction(tx)
        assert e.start_vertex() == a
        assert e.end_vertex() == b
        assert e.get_label() == "foo"
        assertInterface(IEdge, e)
        e_id = e.get_dbId()
        assertInterface(IEdge, self.g.get_edge(e_id))
        self.assertEqual(e_id, self.g.get_edge(e_id).get_dbId())

    def testAddEdgeWithMarkerInterface(self):
        tx = self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo", main_interface=IDummyMarker)
        self.g.stop_transaction(tx)
        assertInterface(IEdge, e)
        assertInterface(IDummyMarker, e)

    def testAddReference(self):
        tx = self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo", main_interface=IDummyReferenceMarker)
        self.g.stop_transaction(tx)
        assertInterface(IEdge, e)
        assertInterface(IReference, e)
        assertInterface(IDummyReferenceMarker, e)

    def testGetEdge(self):
        tx = self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo")
        e_id = e.get_dbId()
        self.assertEqual(e_id, self.g.get_edge(e_id).get_dbId())
        self.g.stop_transaction(tx)

    def testRemoveEdge(self):
        tx = self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo")
        self.g.remove_edge(e)
        self.assertFalse(e in self.g.get_edges())
        self.g.stop_transaction(tx)

    def testGetEdges(self):
        tx = self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        c = self.g.add_vertex()
        e = self.g.add_edge(a, b, "foo")
        f = self.g.add_edge(b, c, "foo")
        for i in self.g.get_edges():
            assertInterface(IEdge, i)
        assertSetEquality([e, f], self.g.get_edges())
        self.g.stop_transaction(tx)

    def testClear(self):
        tx = self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        self.g.add_edge(a, b, "connects")
        self.g.clear()
        root = self.g.get_root_vertex()
        assertSetEquality([root], self.g.get_vertices())
        assertSetEquality([], root.get_properties().keys())
        assertSetEquality([], self.g.get_edges())
        self.g.stop_transaction(tx)

    def testGetRootVertex(self):
        root = self.g.get_root_vertex()
        assertInterface(IVertex, root)
        assertSetEquality([self.g.get_root_vertex()], self.g.get_vertices())

    def testRemvoeRootVertex(self):
        import pytest
        with pytest.raises(DontRemoveRootException):
            tx = self.g.start_transaction()
            root = self.g.get_root_vertex()
            self.g.remove_vertex(root)
            self.g.stop_transaction(tx)

    def testGetProperties(self):
        tx = self.g.start_transaction()
        a = self.g.add_vertex()
        b = self.g.add_vertex()
        e = self.g.add_edge(a, b, "connects")
        ap = {'foo': 42, 'bar': 23}
        a.set_properties(ap)
        ep = {'baz': 42, 'blub': 23}
        e.set_properties(ep)
        assert ap == a.get_properties()
        assert ep == e.get_properties()
        self.g.stop_transaction(tx)

    def testGetProperty(self):
        tx = self.g.start_transaction()
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
        self.g.stop_transaction(tx)

    def testRemoveProperty(self):
        tx = self.g.start_transaction()
        v = self.g.get_root_vertex()
        v.set_property("key", "value")
        assert (v.get_property("key") == "value")
        v.remove_property("key")
        assert "key" not in v.get_properties().keys()
        self.g.stop_transaction(tx)

    def testInOutEdges(self):
        tx = self.g.start_transaction()
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
        self.g.stop_transaction(tx)

    def testGetVertexNone(self):
        tx = self.g.start_transaction()
        assert None == self.g.get_vertex(23)
        self.g.stop_transaction(tx)

    def testEqNone(self):
        assert None != self.g.get_root_vertex()
        assert self.g.get_root_vertex() != None

    def _testTransactionGetVertices(self):
        this_tx = self.g.start_transaction()
        with BlockingWorkerThread() as thread:
            def prep():
                tx = self.g.start_transaction()
                v = self.g.add_vertex()
                return (tx, v.get_dbId())
            (other_tx, v_id) = thread.do(prep)
            try:
                root = self.g.get_root_vertex()
                assertSetEquality(self.g.get_vertices(), [root])
            except:
                thread.do(lambda: self.g.fail_transaction(other_tx))
                raise
            else:
                thread.do(lambda: self.g.stop_transaction(other_tx))
            assertSetEquality(
                self.g.get_vertices(),
                [root, self.g.get_vertex(v_id)])
        self.g.stop_transaction(this_tx)

    def _testTransactionEdges(self):
        prep_tx = self.g.start_transaction()
        v_id = self.g.add_vertex().get_dbId()
        self.g.stop_transaction(prep_tx)

        this_tx = self.g.start_transaction()
        with BlockingWorkerThread() as thread:
            def prep():
                tx = self.g.start_transaction()
                v = self.g.get_vertex(v_id)
                self.g.add_edge(self.g.get_root_vertex(), v, "connects")
                return (tx)
            other_tx = thread.do(prep)

            assertSetEquality(self.g.get_root_vertex().out_edges(), [])
            thread.do(lambda: self.g.stop_transaction(other_tx))
            root_out_node_ids = map(
                lambda e: e.end_vertex().get_dbId(),
                self.g.get_root_vertex().out_edges())
            assertSetEquality(root_out_node_ids, [v_id])
        self.g.stop_transaction(this_tx)

    def _testTransactionOtherTransactionException(self):
        raise Exception("currently broken")
        with BlockingWorkerThread() as thread:
            def f():
                tx = self.g.start_transaction
                return (tx, self.g.add_vertex())
            (other_tx, other_v) = thread.do(f)

            thisTx = self.g.start_transaction()
            self.assertRaises(NotInTransactionException, other_v.get_dbId)
            self.g.stop_transaction(thisTx)

            thread.do(lambda: self.g.stop_transaction(other_tx))


#TODO: nested transactions
#TODO: success
#TODO: failure


class BlockingWorkerThread(object):
    """Thread for testing transactions."""
    def _worker_thread(self):
        while True:
            thunk = self.inputCmds.get()
            try:
                returnValue = thunk()
            except Exception, e:
                print("\nException in BlockingWorkerThread:\n%s" % e)
                self.outputValues.put(e)
            else:
                self.outputValues.put(returnValue)
            finally:
                self.inputCmds.task_done()

    def __enter__(self):
        from Queue import Queue
        from threading import Thread

        self.inputCmds = Queue()
        self.outputValues = Queue()
        self.thread = Thread(target=self._worker_thread)
        self.thread.daemon = True
        self.thread.start()
        return self

    def __exit__(self, a, b, c):
        self.inputCmds.join()
        self.outputValues.join()
        # return False to reraise possible exceptions
        return False

    def do(self, thunk):
        self.inputCmds.put(thunk)
        returnValue = self.outputValues.get()
        self.outputValues.task_done()
        if isinstance(returnValue, Exception):
            raise returnValue
        return returnValue


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


class FieldPropertyTest(unittest.TestCase):

    @classmethod
    def setup_class(self):
        from neo4j import GraphDatabase
        db = GraphDatabase(GRAPHDB_CONNECTION_STRING)
        self.g = EmbeddedGraph(db)

        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(DummyNodeWithFieldsAdapter)

    @classmethod
    def teardown_class(self):
        self.g.shutdown()
        del self.g

    def tearDown(self):
        tx = self.g.start_transaction()
        self.g.clear()
        self.g.stop_transaction(tx)

    def testGetFieldDefault(self):
        #create node
        tx = self.g.start_transaction()
        node = self.g.add_vertex(main_interface=IDummyNodeMarker)
        node_with_fields = IDummyNodeWithFields(node)
        self.g.stop_transaction(tx)
        assert(node_with_fields.first_names == (u"default name",))

    def testGetSetField(self):
        tx = self.g.start_transaction()
        #set attribute
        node = self.g.add_vertex(main_interface=IDummyNodeMarker)
        node_with_fields = IDummyNodeWithFields(node)
        node_with_fields.first_names = (u"test",)
        self.g.stop_transaction(tx)
        assert(node_with_fields.first_names == (u"test",))
        #get attribtute
        v_id = node.get_dbId()
        new_node = self.g.get_vertex(v_id)
        new_node_with_fields = IDummyNodeWithFields(new_node)
        assert(new_node_with_fields.first_names == (u"test",))

    def test_python_list_to_graphdb_converter(self):
        from zope.schema import List
        schema_field = List()
        value = [1]
        from adhocracy.dbgraph.fieldproperty import python_to_db
        value_db = python_to_db(schema_field, value)
        assert(value_db == "[1]")
        from adhocracy.dbgraph.fieldproperty import db_to_python
        value = db_to_python(schema_field, value_db)
        assert(value == [1])

    def test_python_tuple_to_graphdb_converter(self):
        from zope.schema import Tuple
        schema_field = Tuple()
        value = (1,)
        from adhocracy.dbgraph.fieldproperty import python_to_db
        value_db = python_to_db(schema_field, value)
        assert(value_db == "[1]")
        from adhocracy.dbgraph.fieldproperty import db_to_python
        value = db_to_python(schema_field, value_db)
        assert(value == (1,))

    def test_python_dict_to_graphdb_converter(self):
        from zope.schema import Dict
        schema_field = Dict()
        value = {"1": 1}
        from adhocracy.dbgraph.fieldproperty import python_to_db
        value_db = python_to_db(schema_field, value)
        assert value_db == '{"1": 1}'
        from adhocracy.dbgraph.fieldproperty import db_to_python
        value = db_to_python(schema_field, value_db)
        assert(value == {"1": 1})

    def test_python_dict_to_graphdb_converter_assert_string_keys(self):
        from zope.schema import Dict
        schema_field = Dict()
        value = {1: 1}
        from adhocracy.dbgraph.fieldproperty import python_to_db
        import pytest
        with pytest.raises(AssertionError):
            python_to_db(schema_field, value)


if __name__ == "__main__":
    unittest.main()
