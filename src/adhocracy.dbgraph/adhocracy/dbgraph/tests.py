# -*- coding: utf-8 -*-

import unittest
from pyramid import testing

from adhocracy.dbgraph.embeddedgraph import EmbeddedGraph
from adhocracy.dbgraph.embeddedgraph import get_graph
from adhocracy.dbgraph.interfaces import IGraph


GRAPHDB_CONNECTION_STRING = "testdb"


def setUp(**kwargs):
    """
       setUp basic test environment
       proxy to pyramid.testing.setUp(**kwargs)
    """
    testing.tearDown()
    settings = {}
    settings['graphdb_connection_string'] = GRAPHDB_CONNECTION_STRING
    settings.update(kwargs.get('settings', {}))
    kwargs['settings'] = settings
    config = testing.setUp(**kwargs)
    return config


def tearDown(**kwargs):
    """
       tearDown basic test environment with database
       proxy to paramid.testing.tearDown(**kwargs)
    """
    graph = get_graph()
    if graph:
        graph.clear()
        graph.shutdown()
    testing.tearDown(**kwargs)


class DBGGraphUtilityTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()
        self.graph = get_graph()

    def tearDown(self):
        tearDown()

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
        self.g = EmbeddedGraph(GRAPHDB_CONNECTION_STRING)
        # TODO: use clear in setUp and/or teardown

    def testVertices(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        self.assertEqual(a.get_dbId(),
                self.g.get_vertex(a.get_dbId()).get_dbId())
        self.g.stop_transaction()

if __name__ == "__main__":
    unittest.main()
