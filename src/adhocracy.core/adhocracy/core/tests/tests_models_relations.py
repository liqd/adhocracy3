import unittest

from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown
from adhocracy.core.testing import get_graph


class ModelChildRelationTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()
        from repoze.lemonade.testing import registerContentFactory
        from adhocracy.core.models.references import child_factory
        from adhocracy.core.models.references import IChildMarker
        registerContentFactory(child_factory, IChildMarker)
        from adhocracy.core.models.container import container_factory
        from adhocracy.core.models.container import IContainerMarker
        registerContentFactory(container_factory, IContainerMarker)

        from adhocracy.core.models.references import Child
        self.config.registry.registerAdapter(Child)
        self.config.registry.registerAdapter(self._target_class)
        self.graph = get_graph()

    def tearDown(self):
        tearDown()

    @property
    def _target_interface(self):
        from adhocracy.core.models.interfaces import IChildsDict
        return IChildsDict

    @property
    def _target_class(self):
        from adhocracy.core.models.relations import NodeChildsDictAdapter
        return NodeChildsDictAdapter

    def _make_dummy_node(self):
        from adhocracy.core.models.container import IContainerMarker
        from repoze.lemonade.content import create_content
        content = create_content(IContainerMarker)
        return content

    def test_create_adapter(self):
        tx = self.graph.start_transaction()
        parent = self._make_dummy_node()
        self.graph.stop_transaction(tx)
        adapter = self._target_interface(parent)
        self.assert_(isinstance(adapter, self._target_class))
        from zope.interface.verify import verifyObject
        assert(verifyObject(self._target_interface, adapter))
        assert(adapter.context == parent)

    def test_interface_inheritance(self):
        tx = self.graph.start_transaction()
        parent = self._make_dummy_node()
        self.graph.stop_transaction(tx)
        from pyramid_adoptedtraversal.interfaces import IChildsDictLike
        assert(self._target_interface(parent) == IChildsDictLike(parent))

    def test_set_item(self):
        tx = self.graph.start_transaction()
        parent = self._make_dummy_node()
        child = self._make_dummy_node()
        parent_adapter = self._target_interface(parent)
        parent_adapter["g2"] = child
        self.graph.stop_transaction(tx)
        self.assertIsNotNone(parent)
        self.assertIsNotNone(child)
        #self.assertEquals([parent.get_dbId()],
            #map(lambda x: x.get_dbId(), list(child.outV("child"))))
        #assert("g2" in parent_adapter)
        #assert(child.eid == parent_adapter["g2"].eid)
        #assert("not_available" not in parent_adapter)
        #self.assertRaises(KeyError, parent_adapter.__getitem__,\
                                    #("not_available"))
        #assert(parent.__parent__ is None)
        #assert(child.__parent__ is not None)
        #assert(child.__parent__.eid == parent.eid)

    def test_del_item(self):
        tx = self.graph.start_transaction()
        parent = self._make_dummy_node()
        child = self._make_dummy_node()
        parent_adapter = self._target_interface(parent)
        parent_adapter["g2"] = child
        del parent_adapter["g2"]
        self.graph.stop_transaction(tx)
        assert("g2" not in parent_adapter)
