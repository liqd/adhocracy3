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

    def test_adhocracyroot_factory(self):
        from adhocracy.core.models.interfaces import IAdhocracyRoot
        from adhocracy.core.models.utilities import adhocracyroot_factory
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(adhocracyroot_factory, IAdhocracyRoot)

        from adhocracy.core.models.interfaces import IAdhocracyRoot
        from adhocracy.core.models.adhocracyroot import AdhocracyRoot
        from repoze.lemonade.content import create_content
        adhocracyroot = create_content(IAdhocracyRoot)
        self.assert_(isinstance(adhocracyroot, AdhocracyRoot))

    def test_container_factory(self):
        from adhocracy.core.models.interfaces import IContainer
        from adhocracy.core.models.utilities import container_factory
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(container_factory, IContainer)

        from adhocracy.core.models.container import Container
        from repoze.lemonade.content import create_content
        container1 = create_content(IContainer, name=u"g1")
        self.assert_(isinstance(container1, Container))

    def test_child_factory(self):
        from adhocracy.core.models.interfaces import IChild
        from adhocracy.core.models.utilities import child_factory
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(child_factory, IChild)
        #TODO: use Dummy content instead of Container
        #TODO: move all those factory test to the model tests...
        from adhocracy.core.models.interfaces import IContainer
        from adhocracy.core.models.utilities import container_factory
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(container_factory, IContainer)

        from adhocracy.core.models.interfaces import IChild
        from adhocracy.core.models.relations import Child
        from repoze.lemonade.content import create_content
        parent = create_content(IContainer, name=u"p")
        child = create_content(IContainer, name=u"child1_uid")
        child_relation = create_content(IChild,
                                        child=child,
                                        parent=parent,
                                        child_name=u'child')
        self.assert_(isinstance(child_relation, Child))
