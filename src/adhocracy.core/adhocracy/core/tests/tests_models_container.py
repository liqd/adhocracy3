import unittest

from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown
from adhocracy.core.testing import get_graph


class ContainerModelTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()
        from adhocracy.core.models.container import container_factory
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(container_factory,\
                               self._target_marker_interface)
        from adhocracy.core.models.container import ContainerLocationAware
        self.config.registry.registerAdapter(ContainerLocationAware)
        from adhocracy.core.models.container import Container
        self.config.registry.registerAdapter(Container)
        self.graph = get_graph()

    def tearDown(self):
        tearDown()

    @property
    def _target_marker_interface(self):
        from adhocracy.core.models.container import IContainerMarker
        return IContainerMarker

    @property
    def _target_interface(self):
        from adhocracy.core.models.container import IContainer
        return IContainer

    def _make_one(self):
        from repoze.lemonade.content import create_content
        content = create_content(self._target_marker_interface)
        return content

    def test_factory_register(self):
        from repoze.lemonade.content import get_content_types
        assert(self._target_marker_interface in get_content_types())

    def test_create_content(self):
        tx = self.graph.start_transaction()
        content = self._make_one()
        self.graph.stop_transaction(tx)
        from zope.interface.verify import verifyObject
        from adhocracy.dbgraph.interfaces import INode
        assert(INode.providedBy(content))
        assert(verifyObject(INode, content))
        assert(self._target_marker_interface.providedBy(content))
        content = self._target_interface(content)
        assert(verifyObject(self._target_interface, content))
