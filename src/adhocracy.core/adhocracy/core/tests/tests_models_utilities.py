import unittest

from zope.interface.verify import verifyObject
from pyramid.threadlocal import get_current_registry
from pyramid import testing

from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown

from adhocracy.core.models.interfaces import IGraphConnection


class UtilitiesTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()

    def tearDown(self):
        tearDown()

    def test_get_graph_database_connection(self):
        registry = get_current_registry()
        graph1 = registry.getUtility(IGraphConnection)
        self.assert_(IGraphConnection.providedBy(graph1))
        self.assert_(verifyObject(IGraphConnection, graph1))
        graph2 = registry.getUtility(IGraphConnection)
        self.assert_(graph1 is graph2)
