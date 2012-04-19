import unittest

from zope.interface.verify import verifyObject
from pyramid import testing
from pyramid.threadlocal import get_current_registry

from adhocracy.core.models.interfaces import IGraphConnection


class UtilitiesTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={'rexster_uri':"http://localhost:8182/graphs/testgraph"})
        self.config.include('pyramid_zcml')
        self.config.load_zcml('adhocracy.core.models:utilities.zcml')

    def tearDown(self):
        registry = get_current_registry()
        graph = registry.getUtility(IGraphConnection)
        graph.clear()
        testing.tearDown()

    def test_get_graph_database_connection(self):
        registry = get_current_registry()
        graph1 = registry.getUtility(IGraphConnection)
        self.assert_(IGraphConnection.providedBy(graph1))
        self.assert_(verifyObject(IGraphConnection, graph1))
        graph2 = registry.getUtility(IGraphConnection)
        self.assert_(graph1 is graph2)

    def test_adhocracyroot_factory(self):
        from adhocracy.core.models.interfaces import IAdhocracyRoot
        from adhocracy.core.models.adhocracyroot import AdhocracyRoot
        from repoze.lemonade.content import create_content
        adhocracyroot = create_content(IAdhocracyRoot)
        self.assert_(isinstance(adhocracyroot, AdhocracyRoot))

    def test_container_factory(self):
        from adhocracy.core.models.interfaces import IContainer
        from adhocracy.core.models.container import Container
        from repoze.lemonade.content import create_content
        container1 = create_content(IContainer, name=u"g1")
        self.assert_(isinstance(container1, Container))

    def test_child_factory(self):
        from adhocracy.core.models.interfaces import IContainer
        from adhocracy.core.models.interfaces import IChild
        from adhocracy.core.models.relations import Child
        from repoze.lemonade.content import create_content
        parent = create_content(IContainer, name=u"p")
        child1 = create_content(IContainer, name=u"child1_uid")
        child_relation = create_content(IChild,
                                        child=child1,
                                        parent=parent,
                                        child_name=u'child1')
        self.assert_(isinstance(child_relation, Child))
