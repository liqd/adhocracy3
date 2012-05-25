import unittest

from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown
from adhocracy.core.testing import get_graph


class ChildReferenceTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()
        from adhocracy.core.models.references import child_factory
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(child_factory, self._target_marker_interface)
        from adhocracy.core.models.references import Child
        self.config.registry.registerAdapter(Child)
        self.graph = get_graph()

    def tearDown(self):
        tearDown()

    @property
    def _target_marker_interface(self):
        from adhocracy.core.models.references import IChildMarker
        return IChildMarker

    @property
    def _target_interface(self):
        from adhocracy.core.models.references import IChild
        return IChild

    def _make_one(self, parent=None, child=None, child_name=u""):
        from repoze.lemonade.content import create_content
        content = create_content(self._target_marker_interface,\
                            parent=parent, child=child, child_name=child_name)
        return content

    def _make_dummy_node(self, name=u"node"):
        from adhocracy.core.testing import IDummyNode
        return self.graph.add_vertex(IDummyNode)

    def test_factory_register(self):
        from repoze.lemonade.content import get_content_types
        assert(self._target_marker_interface in get_content_types())

    def test_create_content(self):
        tx = self.graph.start_transaction()
        parent = self._make_dummy_node()
        child = self._make_dummy_node()
        content = self._make_one(parent, child, child_name=u"name")
        self.graph.stop_transaction(tx)
        from zope.interface.verify import verifyObject
        from adhocracy.dbgraph.interfaces import IReference
        assert(IReference.providedBy(content))
        assert(verifyObject(IReference, content))
        assert(self._target_marker_interface.providedBy(content))
        assert(content.start_vertex().get_dbId() == child.get_dbId())
        assert(content.end_vertex().get_dbId() == parent.get_dbId())
        assert(content.get_label() == "child")
        content = self._target_interface(content)
        assert(verifyObject(self._target_interface, content))
