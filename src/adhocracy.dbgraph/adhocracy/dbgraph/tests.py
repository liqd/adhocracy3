
import unittest
from adhocracy.dbgraph.EmbeddedGraphConnection import EmbeddedGraphConnection


class DBGraphTestSuite(unittest.TestCase):

    def setUp(self):
        self.graph = EmbeddedGraphConnection("testdb")
        self.g = self.graph
        # TODO: use clear in setUp and/or teardown

    def testVertices(self):
        g.startTransaction()
        a = g.addVertex()
        self.assertEqual(a.getDBId(), g.getVertex(a.getDBId()).getDBId())

if __name__ == "__main__":
    unittest.main()
