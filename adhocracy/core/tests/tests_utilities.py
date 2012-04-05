import unittest

from zope.interface.verify import verifyObject
from pyramid import testing
from pyramid.threadlocal import get_current_registry

from adhocracy.core.models.interfaces import IGraphConnection



class UtilitiesTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_zcml')
        import adhocracy.core
        self.config.load_zcml('adhocracy.core.models:utilities.zcml')

    def tearDown(self):
        testing.tearDown()

    def test_get_graph_database_connection(self):
        registry = get_current_registry()
        graph1 = registry.getUtility(IGraphConnection)
        assert(IGraphConnection.providedBy(graph1))
        assert(verifyObject(IGraphConnection, graph1))
        graph2 = registry.getUtility(IGraphConnection)
        assert(graph1 is graph2)

