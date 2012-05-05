# -*- coding: utf-8 -*-

import unittest

from adhocracy.dbgraph.embeddedgraph import EmbeddedGraph


class DBGraphTestSuite(unittest.TestCase):

    def setUp(self):
        self.g = EmbeddedGraph("testdb")
        # TODO: use clear in setUp and/or teardown

    def testVertices(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        self.assertEqual(a.get_dbId(),
                self.g.get_vertex(a.get_dbId()).get_dbId())
        self.g.stop_transaction()

if __name__ == "__main__":
    unittest.main()
