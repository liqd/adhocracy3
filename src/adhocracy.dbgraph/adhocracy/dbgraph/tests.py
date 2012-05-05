import unittest
from adhocracy.dbgraph.embeddedgraph import EmbeddedGraph


class DBGraphTestSuite(unittest.TestCase):

    def setUp(self):
        self.g = EmbeddedGraph("testdb")
        # TODO: use clear in setUp and/or teardown

    def testVertices(self):
        self.g.start_transaction()
        a = self.g.add_vertex()
        self.assertEqual(a.get_dbId(), self.g.getVertex(a.get_dbId()).get_dbId())

if __name__ == "__main__":
    unittest.main()
